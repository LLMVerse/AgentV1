// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FeePool {
    address public owner;
    mapping(address => uint256) public balances;
    uint256 public currentEpoch;

    event FeeReceived(address indexed from, uint256 amount);
    event Distributed(address indexed to, uint256 amount);
    event EpochStarted(uint256 indexed epoch);
    event OwnerSwapped(address indexed oldOwner, address indexed newOwner);

    constructor() {
        owner = msg.sender;
        currentEpoch = 1;
    }

    function payFee() external payable {
        require(msg.value > 0, "No fee sent");
        balances[msg.sender] += msg.value;
        emit FeeReceived(msg.sender, msg.value);
    }

    // Distribute a specific amount to a single address (legacy/simple)
    function distribute(address to, uint256 amount) external {
        require(msg.sender == owner, "Only owner");
        require(address(this).balance >= amount, "Insufficient balance");
        payable(to).transfer(amount);
        emit Distributed(to, amount);
    }

    // Pro-rata distribution: distribute to multiple recipients in one call
    // NOTE: The backend does calculate the correct payouts and call this function.
    function distributeProRata(address[] calldata recipients, uint256[] calldata amounts) external {
        require(msg.sender == owner, "Only owner");
        require(recipients.length == amounts.length, "Mismatched arrays");
        uint256 total = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            total += amounts[i];
        }
        require(address(this).balance >= total, "Insufficient balance for distribution");
        for (uint256 i = 0; i < recipients.length; i++) {
            payable(recipients[i]).transfer(amounts[i]);
            emit Distributed(recipients[i], amounts[i]);
        }
    }

    // Start a new epoch (for future extensibility)
    function startNewEpoch() external {
        require(msg.sender == owner, "Only owner");
        currentEpoch += 1;
        emit EpochStarted(currentEpoch);
    }

    // Swap owner (for protocol upgrades or governance)
    function swapOwner(address newOwner) external {
        require(msg.sender == owner, "Only owner");
        require(newOwner != address(0), "Invalid new owner");
        emit OwnerSwapped(owner, newOwner);
        owner = newOwner;
    }

}
