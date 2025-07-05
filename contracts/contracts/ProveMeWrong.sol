// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Clones} from "@openzeppelin/contracts/proxy/Clones.sol";

import {ContractRegistry} from "@flarenetwork/flare-periphery-contracts/coston2/ContractRegistry.sol";
import {IWeb2Json} from "@flarenetwork/flare-periphery-contracts/coston2/IWeb2Json.sol";

import {IPMW20} from "./IPMW20.sol";
import {PMW20} from "./PMW20.sol";
import {PMWPool} from "./PMWPool.sol";

contract ProveMeWrong {
    struct Market {
        bytes32 requestHash;
        address yes;
        address no;
        uint256 yesPrice;
        uint256 noPrice;
        address pool;
        // 0 = no, 1 = yes, 2 = unknown
        uint256 outcome;
    }

    uint256 private constant PRICE_SCALE = 1e18;
    uint256 private constant CURVE_FACTOR = 1e15; // 0.1% curve steepness
    uint256 private constant FEE_PERCENTAGE = 1e15; // 0.1% fee (1e15 = 0.1% of 1e18)

    address public immutable pmw20Implementation;
    address public immutable pmwPoolImplementation;

    // Market ID => Market
    mapping(bytes32 => Market) private _markets;

    struct ResolutionData {
        // 0 = no, 1 = yes, 2 = unknown
        uint256 outcome;
    }

    constructor() {
        pmw20Implementation = address(new PMW20());
        pmwPoolImplementation = address(new PMWPool());
    }

    // DEBUG
    /*
    function createPoolAndMarket(
        address asset,
        address owner,
        bytes32 marketId,
        bytes32 requestHash,
        uint256 yesPrice,
        uint256 noPrice
    ) external { 
        address pool = createPool(asset, owner);
        createMarket(marketId, requestHash, yesPrice, noPrice, pool);
    }
    */
   
    function createPool(address asset, address owner) public returns (address) {
        address pool = Clones.clone(pmwPoolImplementation);
        PMWPool(pool).initialize(
            asset,
            address(this),
            pmw20Implementation,
            owner
        );

        return pool;
    }

    function createMarket(
        bytes32 marketId,
        bytes32 requestHash,
        uint256 yesPrice,
        uint256 noPrice,
        address pool
    ) public {
        if (_marketExists(marketId)) {
            revert("Market already exists");
        }

        if (PMWPool(pool).owner() != msg.sender) {
            revert("Pool not owned by caller");
        }

        if (yesPrice + noPrice != PRICE_SCALE) {
            revert("Prices must sum to 100%");
        }
        
        address yes = Clones.clone(pmw20Implementation);
        IPMW20(yes).initialize(
            "yes",
            "YES",
            address(this)
        );

        address no = Clones.clone(pmw20Implementation);
        IPMW20(no).initialize(
            "no",
            "NO",
            address(this)
        );

        _markets[marketId] = Market({
            requestHash: requestHash,
            yes: yes,
            no: no,
            yesPrice: yesPrice,
            noPrice: noPrice,
            pool: pool,
            outcome: 2
        });
    }

    function getMarket(bytes32 marketId) public view returns (address, address, uint256, uint256, address, uint256) {
        return (
            _markets[marketId].yes,
            _markets[marketId].no,
            _markets[marketId].yesPrice,
            _markets[marketId].noPrice,
            _markets[marketId].pool,
            _markets[marketId].outcome
        );
    }

    function mint(
        bytes32 marketId,
        uint256 amount,
        bool outcome
    ) external {
        if (!_marketExists(marketId)) {
            revert("Market does not exist");
        }

        if (_marketResolved(marketId)) {
            revert("Market already resolved");
        }

        if (amount == 0) {
            revert("Amount must be greater than 0");
        }

        // Calculate fee (0.1% of the bet amount)
        uint256 feeAmount = (amount * FEE_PERCENTAGE) / PRICE_SCALE;
        uint256 betAmount = amount - feeAmount;

        IERC20(PMWPool(_markets[marketId].pool).asset()).transferFrom(
            msg.sender,
            _markets[marketId].pool,
            amount
        );

        // Calculate tokens to mint based on current prices (using amount after fee)
        uint256 tokensToMint;
        if (outcome == true) {
            tokensToMint = (betAmount * PRICE_SCALE) / _markets[marketId].yesPrice;
        } else {
            tokensToMint = (betAmount * PRICE_SCALE) / _markets[marketId].noPrice;
        }

        // Mint tokens representing potential winnings
        if (outcome == true) {
            IPMW20(_markets[marketId].yes).mint(msg.sender, tokensToMint);
        } else {
            IPMW20(_markets[marketId].no).mint(msg.sender, tokensToMint);
        }

        // Update prices using bonding curve adjustment
        _updatePricesWithBondingCurve(marketId, outcome);
    }

    function redeem(
        bytes32 marketId,
        address account
    ) external {
        if (!_marketExists(marketId)) {
            revert("Market does not exist");
        }

        if(!_marketResolved(marketId)) {
            revert("Market not resolved");
        }

        address token = _markets[marketId].outcome == 1 ? _markets[marketId].yes : _markets[marketId].no;
        
        uint256 balance = IPMW20(token).balanceOf(account);
        if(balance == 0) {
            revert("No tokens to redeem");
        }

        IPMW20(token).burnFrom(account, balance);
        IERC20(PMWPool(_markets[marketId].pool).asset()).transfer(
            account,
            balance
        );
    }

    function _updatePricesWithBondingCurve(bytes32 marketId, bool outcome) private {
        Market storage market = _markets[marketId];
        
        uint256 yesSupply = IPMW20(market.yes).totalSupply();
        uint256 noSupply = IPMW20(market.no).totalSupply();
        uint256 totalSupply = yesSupply + noSupply;

        // Calculate adjustment based on bonding curve
        uint256 adjustmentFactor = CURVE_FACTOR;
        if (totalSupply > PRICE_SCALE) {
            // Decrease adjustment rate as supply increases
            adjustmentFactor = (CURVE_FACTOR * PRICE_SCALE) / 
                             (PRICE_SCALE + (totalSupply - PRICE_SCALE) / 10);
        }

        // Calculate price adjustments based on the minting action
        if (outcome == true) {
            // Minting yes tokens: increase yes price, decrease no price
            uint256 yesIncrease = (adjustmentFactor * market.yesPrice) / PRICE_SCALE;
            uint256 noDecrease = (adjustmentFactor * market.noPrice) / PRICE_SCALE;
            
            market.yesPrice = market.yesPrice + yesIncrease;
            market.noPrice = market.noPrice - noDecrease;
        } else {
            // Minting no tokens: increase no price, decrease yes price
            uint256 noIncrease = (adjustmentFactor * market.noPrice) / PRICE_SCALE;
            uint256 yesDecrease = (adjustmentFactor * market.yesPrice) / PRICE_SCALE;
            
            market.noPrice = market.noPrice + noIncrease;
            market.yesPrice = market.yesPrice - yesDecrease;
        }

        // Normalize to ensure prices sum to PRICE_SCALE
        uint256 totalPrice = market.yesPrice + market.noPrice;
        market.yesPrice = (market.yesPrice * PRICE_SCALE) / totalPrice;
        market.noPrice = (market.noPrice * PRICE_SCALE) / totalPrice;
    }

    function resolveMarket(
        bytes32 marketId,
        IWeb2Json.Proof calldata data
    ) external {
        if (!_isJsonApiProofValid(data)) {
            revert("Invalid proof");
        }

        if (!_marketExists(marketId)) {
            revert("Market does not exist");
        }

        if (_marketResolved(marketId)) {
            revert("Market already resolved");
        }

        if (
            _markets[marketId].requestHash !=
            _hashRequest(
                data.data.requestBody.url, 
                data.data.requestBody.httpMethod,
                data.data.requestBody.headers, 
                data.data.requestBody.queryParams, 
                data.data.requestBody.body,
                data.data.requestBody.postProcessJq, 
                data.data.requestBody.abiSignature
            )
        ) {
            revert("Invalid request hash");
        }

        ResolutionData memory resolutionData = abi.decode(
            data.data.responseBody.abiEncodedData,
            (ResolutionData)
        );
        uint256 outcome = resolutionData.outcome;

        if (outcome == 2) {
            revert("Market not resolved");
        }

        _markets[marketId].outcome = outcome;
    }

    function _marketExists(bytes32 marketId) private view returns (bool) {
        return _markets[marketId].requestHash != bytes32(0);
    }

    function _marketResolved(bytes32 marketId) internal view returns (bool) {
        return _markets[marketId].outcome != 2;
    }

    function _hashRequest(
        string memory url,
        string memory httpMethod,
        string memory headers,
        string memory queryParams,
        string memory body,
        string memory postProcessJq,
        string memory abiSignature
    ) private pure returns (bytes32) {
        return keccak256(abi.encode(
            url, 
            httpMethod,
            headers, 
            queryParams, 
            body, 
            postProcessJq, 
            abiSignature
        ));
    }

    function _isJsonApiProofValid(
        IWeb2Json.Proof calldata _proof
    ) private view returns (bool) {
        // Inline the check for now until we have an official contract deployed
        return ContractRegistry.getFdcVerification().verifyJsonApi(_proof);
    }
}
