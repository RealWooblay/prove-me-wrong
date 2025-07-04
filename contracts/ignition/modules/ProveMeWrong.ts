import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("ProveMeWrong", (m) => {
    const proveMeWrong = m.contract("ProveMeWrong");

    /*
    m.call(proveMeWrong, "createPoolAndMarket", [
        "0xC1A5B41512496B80903D1f32d6dEa3a73212E71F",
        "0xA3c41DEa8052124Bc2575ed96e56e9AeC4919195",
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "500000000000000000",
        "500000000000000000"
    ]);
    */

    m.call(proveMeWrong, "createPool", [
        "0xC1A5B41512496B80903D1f32d6dEa3a73212E71F",
        "0xA3c41DEa8052124Bc2575ed96e56e9AeC4919195"
    ]);

    return { proveMeWrong };
});