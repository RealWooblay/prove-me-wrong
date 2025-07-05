import type { HardhatUserConfig } from "hardhat/config";

import hardhatToolboxViemPlugin from "@nomicfoundation/hardhat-toolbox-viem";
import { configVariable } from "hardhat/config";
import hardhatVerify from "@nomicfoundation/hardhat-verify";

const config: HardhatUserConfig = {
  verify: {
    etherscan: {
      apiKey: "coston2", // apiKey is not required, just set a placeholder
    },
  },
  /*
   * In Hardhat 3, plugins are defined as part of the Hardhat config instead of
   * being based on the side-effect of imports.
   *
   * Note: A `hardhat-toolbox` like plugin for Hardhat 3 hasn't been defined yet,
   * so this list is larger than what you would normally have.
   */
  plugins: [
    hardhatToolboxViemPlugin,
    hardhatVerify
  ],
  solidity: {
    /*
     * Hardhat 3 supports different build profiles, allowing you to configure
     * different versions of `solc` and its settings for various use cases.
     *
     * Note: Using profiles is optional, and any Hardhat 2 `solidity` config
     * is still valid in Hardhat 3.
     */
    profiles: {
      /*
       * The default profile is used when no profile is defined or specified
       * in the CLI or by the tasks you are running.
       */
      default: {
        version: "0.8.28",
      },
      /*
       * The production profile is meant to be used for deployments, providing
       * more control over settings for production builds and taking some extra
       * steps to simplify the process of verifying your contracts.
       */
      production: {
        version: "0.8.28",
        settings: {
          optimizer: {
            enabled: false
          },
        },
      },
    },
  },
  /*
   * The `networks` configuration is mostly compatible with Hardhat 2.
   * The key differences right now are:
   *
   * - You must set a `type` for each network, which is either `edr` or `http`,
   *   allowing you to have multiple simulated networks.
   *
   * - You can set a `chainType` for each network, which is either `generic`,
   *   `l1`, or `optimism`. This has two uses. It ensures that you always
   *   connect to the network with the right Chain Type. And, on `edr`
   *   networks, it makes sure that the simulated chain behaves exactly like the
   *   real one. More information about this can be found in the test files.
   *
   * - The `accounts` field of `http` networks can also receive Configuration
   *   Variables, which are values that only get loaded when needed. This allows
   *   Hardhat to still run despite some of its config not being available
   *   (e.g., a missing private key or API key). More info about this can be
   *   found in the "Sending a Transaction to Optimism Sepolia" of the README.
   */
  networks: {
    coston2: {
      type: "http",
      chainType: "l1",
      url: 'https://coston2-api.flare.network/ext/bc/C/rpc',
      accounts: ["b81faea7d21760bdd498e56b570c8cf7351c1aa851efe4b69da6c8bd0cf0a53f"]
    },
  },
};

export default config;
