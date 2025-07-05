export const ProveMeWrongAbi = [
  {
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [],
    "name": "FailedDeployment",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "balance",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "needed",
        "type": "uint256"
      }
    ],
    "name": "InsufficientBalance",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "marketId",
        "type": "bytes32"
      },
      {
        "internalType": "bytes32",
        "name": "requestHash",
        "type": "bytes32"
      },
      {
        "internalType": "string",
        "name": "name",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "symbol",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "yesPrice",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "noPrice",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "pool",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "expiry",
        "type": "uint256"
      }
    ],
    "name": "createMarket",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "asset",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      }
    ],
    "name": "createPool",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "marketId",
        "type": "bytes32"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "bool",
        "name": "outcome",
        "type": "bool"
      }
    ],
    "name": "mint",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "pmw20Implementation",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "pmwPoolImplementation",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "marketId",
        "type": "bytes32"
      },
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "redeem",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "marketId",
        "type": "bytes32"
      },
      {
        "components": [
          {
            "internalType": "bytes32[]",
            "name": "merkleProof",
            "type": "bytes32[]"
          },
          {
            "components": [
              {
                "internalType": "bytes32",
                "name": "attestationType",
                "type": "bytes32"
              },
              {
                "internalType": "bytes32",
                "name": "sourceId",
                "type": "bytes32"
              },
              {
                "internalType": "uint64",
                "name": "votingRound",
                "type": "uint64"
              },
              {
                "internalType": "uint64",
                "name": "lowestUsedTimestamp",
                "type": "uint64"
              },
              {
                "components": [
                  {
                    "internalType": "string",
                    "name": "url",
                    "type": "string"
                  },
                  {
                    "internalType": "string",
                    "name": "httpMethod",
                    "type": "string"
                  },
                  {
                    "internalType": "string",
                    "name": "headers",
                    "type": "string"
                  },
                  {
                    "internalType": "string",
                    "name": "queryParams",
                    "type": "string"
                  },
                  {
                    "internalType": "string",
                    "name": "body",
                    "type": "string"
                  },
                  {
                    "internalType": "string",
                    "name": "postProcessJq",
                    "type": "string"
                  },
                  {
                    "internalType": "string",
                    "name": "abiSignature",
                    "type": "string"
                  }
                ],
                "internalType": "struct IWeb2Json.RequestBody",
                "name": "requestBody",
                "type": "tuple"
              },
              {
                "components": [
                  {
                    "internalType": "bytes",
                    "name": "abiEncodedData",
                    "type": "bytes"
                  }
                ],
                "internalType": "struct IWeb2Json.ResponseBody",
                "name": "responseBody",
                "type": "tuple"
              }
            ],
            "internalType": "struct IWeb2Json.Response",
            "name": "data",
            "type": "tuple"
          }
        ],
        "internalType": "struct IWeb2Json.Proof",
        "name": "data",
        "type": "tuple"
      },
      {
        "internalType": "bytes32",
        "name": "requestHashSalt",
        "type": "bytes32"
      }
    ],
    "name": "resolveMarket",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
] as const;