// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {Initializable} from "@openzeppelin/contracts/proxy/utils/Initializable.sol";
import {Clones} from "@openzeppelin/contracts/proxy/Clones.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import {IPMW20} from "./IPMW20.sol";

contract PMWPool is Initializable {
    address private _asset;
    address private _lpToken;

    address private _owner;

    constructor() {}

    function initialize(
        address initAsset,
        address assetSpender,
        address lpTokenImplementation,
        address initOwner
    ) external initializer {
        _asset = initAsset;
        IERC20(_asset).approve(assetSpender, type(uint256).max);

        _lpToken = Clones.clone(lpTokenImplementation);
        IPMW20(_lpToken).initialize(
            "PMW LP",
            "PMW-LP",
            address(this)
        );

        _owner = initOwner;
    }

    function addLiquidity(uint256 amount, address lpTokenRecipient) external {
        IERC20(_asset).transferFrom(msg.sender, address(this), amount);
        IPMW20(_lpToken).mint(lpTokenRecipient, amount);
    }

    function removeLiquidity(uint256 amount, address assetRecipient) external {
        IPMW20(_lpToken).burnFrom(msg.sender, amount);
        IERC20(_asset).transfer(assetRecipient, amount);
    } 

    function asset() external view returns (address) {
        return _asset;
    }

    function lpToken() external view returns (address) {
        return _lpToken;
    }

    function owner() external view returns (address) {
        return _owner;
    }
}