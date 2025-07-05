// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {ERC20, IERC20Metadata} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Initializable} from "@openzeppelin/contracts/proxy/utils/Initializable.sol";

import {IPMW20} from "./IPMW20.sol";

contract PMW20 is
    ERC20,
    ERC20Burnable,
    Ownable,
    Initializable,
    IPMW20
{
    string private _name;
    string private _symbol;

    constructor() ERC20("", "") Ownable(address(1)) {}

    function initialize(
        string memory initName,
        string memory initSymbol,
        address initOwner
    ) external override initializer {
        _name = initName;
        _symbol = initSymbol;

        _transferOwnership(initOwner);
    }

    function mint(address to, uint256 amount) external override onlyOwner {
        _mint(to, amount);
    }

    function burn(uint256 amount) public override(ERC20Burnable, IPMW20) {
        ERC20Burnable.burn(amount);
    }

    function burnFrom(
        address from,
        uint256 amount
    ) public override(ERC20Burnable, IPMW20) {
        if(msg.sender == owner()) {
            _burn(from, amount);
        } else {
            super.burnFrom(from, amount);
        }
    }

    function name()
        public
        view
        override(ERC20, IERC20Metadata)
        returns (string memory)
    {
        return _name;
    }

    function symbol()
        public
        view
        override(ERC20, IERC20Metadata)
        returns (string memory)
    {
        return _symbol;
    }
}
