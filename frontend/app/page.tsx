"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function ProveMeWrong() {
  const [depositAmount, setDepositAmount] = useState("")
  const [isConnected, setIsConnected] = useState(false)

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 relative overflow-hidden">
      {/* Floating background elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-blue-500/5 rounded-full blur-xl"></div>
      <div className="absolute top-40 right-20 w-48 h-48 bg-blue-400/5 rounded-full blur-2xl"></div>
      <div className="absolute bottom-20 left-1/3 w-40 h-40 bg-blue-300/5 rounded-full blur-xl"></div>

      {/* Header */}
      <header className="flex justify-between items-center p-8 relative z-10">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
          Prove Me Wrong
        </h1>
      </header>

      <div className="container mx-auto px-8 space-y-16 relative z-10">
        {/* Hero Section - Creative Layout */}
        <section className="py-16 slide-up">
          <div className="grid lg:grid-cols-2 gap-12 items-center max-w-7xl mx-auto">
            {/* Left side - Main content */}
            <div className="space-y-8">
              <div className="relative">
                <h2 className="text-7xl font-black mb-6 leading-tight">
                  <span className="block text-white">Turn Your</span>
                  <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 transform -rotate-2 inline-block">
                    Predictions
                  </span>
                  <span className="block text-white">Into</span>
                  <span className="block text-transparent bg-clip-text bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 transform rotate-1 inline-block">
                    Markets
                  </span>
                </h2>
                <div className="absolute -top-4 -right-4 w-8 h-8 bg-yellow-400 rounded-full animate-bounce"></div>
                <div className="absolute -bottom-2 -left-2 w-6 h-6 bg-blue-400 rounded-full animate-pulse"></div>
              </div>

              <p className="text-2xl text-slate-300 leading-relaxed">
                Create prediction markets directly on Twitter. Post a claim, let others bet against you,
                and let AI determine the outcome.
                <span className="text-yellow-400 font-bold"> Prove them wrong or admit defeat.</span>
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  onClick={() => window.open("/api/download-extension", "_blank")}
                  className="bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-black px-8 py-4 rounded-2xl font-bold shadow-lg shadow-yellow-500/25 hover:shadow-yellow-500/40 transition-all duration-300 text-lg transform hover:scale-105"
                >
                  🚀 Get Extension
                </Button>
                <Button
                  onClick={() => window.open("https://twitter.com/RealWooblay", "_blank")}
                  className="bg-slate-800 hover:bg-slate-700 text-white px-8 py-4 rounded-2xl font-bold transition-all duration-300 text-lg border-2 border-slate-600 hover:border-slate-500"
                >
                  🐦 See Examples
                </Button>
              </div>
            </div>

            {/* Right side - Visual elements */}
            <div className="relative">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-3xl p-6 border border-blue-400/30 transform rotate-3 hover:rotate-0 transition-transform duration-500">
                    <div className="text-4xl mb-2">🎯</div>
                    <div className="text-sm font-bold text-blue-400">Active Markets</div>
                    <div className="text-2xl font-bold">1,247</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-500/20 to-blue-600/20 rounded-3xl p-6 border border-green-400/30 transform -rotate-2 hover:rotate-0 transition-transform duration-500">
                    <div className="text-4xl mb-2">💰</div>
                    <div className="text-sm font-bold text-green-400">Total Volume</div>
                    <div className="text-2xl font-bold">$2.45M</div>
                  </div>
                </div>
                <div className="space-y-4 mt-8">
                  <div className="bg-gradient-to-br from-purple-500/20 to-pink-600/20 rounded-3xl p-6 border border-purple-400/30 transform -rotate-1 hover:rotate-0 transition-transform duration-500">
                    <div className="text-4xl mb-2">🤖</div>
                    <div className="text-sm font-bold text-purple-400">AI Accuracy</div>
                    <div className="text-2xl font-bold">94.2%</div>
                  </div>
                  <div className="bg-gradient-to-br from-orange-500/20 to-red-600/20 rounded-3xl p-6 border border-orange-400/30 transform rotate-2 hover:rotate-0 transition-transform duration-500">
                    <div className="text-4xl mb-2">🏆</div>
                    <div className="text-sm font-bold text-orange-400">Predictors</div>
                    <div className="text-2xl font-bold">8,472</div>
                  </div>
                </div>
              </div>
              <div className="absolute -top-4 -right-4 w-12 h-12 bg-yellow-400 rounded-full animate-bounce" style={{ animationDelay: '0.5s' }}></div>
              <div className="absolute -bottom-4 -left-4 w-8 h-8 bg-blue-400 rounded-full animate-pulse"></div>
            </div>
          </div>
        </section>

        {/* How It Works - Looney Tunes Style */}
        <section className="slide-up">
          <div className="text-center mb-16">
            <div className="relative inline-block">
              <h2 className="text-6xl font-black mb-4">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 transform -rotate-1 inline-block">
                  How It
                </span>
                <span className="text-white block">Works</span>
              </h2>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-400 rounded-full animate-bounce"></div>
              <div className="absolute -bottom-2 -left-2 w-4 h-4 bg-blue-400 rounded-full animate-pulse"></div>
            </div>
            <p className="text-2xl text-slate-400">Three wild steps to start predicting</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="relative group">
              <div className="bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-3xl p-8 border border-blue-400/30 transform rotate-3 group-hover:rotate-0 transition-all duration-500 hover:scale-110">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500/30 to-purple-600/30 rounded-3xl flex items-center justify-center mx-auto mb-6 transform -rotate-3 group-hover:rotate-0 transition-transform duration-500">
                  <span className="text-5xl">📱</span>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-blue-400 text-center">Install Extension</h3>
                <p className="text-slate-300 text-center leading-relaxed">Add our browser extension to see prediction markets on Twitter</p>
                <div className="absolute -top-2 -right-2 w-4 h-4 bg-blue-400 rounded-full animate-pulse"></div>
              </div>
            </div>

            <div className="relative group mt-8">
              <div className="bg-gradient-to-br from-green-500/20 to-blue-600/20 rounded-3xl p-8 border border-green-400/30 transform -rotate-2 group-hover:rotate-0 transition-all duration-500 hover:scale-110">
                <div className="w-20 h-20 bg-gradient-to-br from-green-500/30 to-blue-600/30 rounded-3xl flex items-center justify-center mx-auto mb-6 transform rotate-2 group-hover:rotate-0 transition-transform duration-500">
                  <span className="text-5xl">🎯</span>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-green-400 text-center">Create & Share Markets</h3>
                <p className="text-slate-300 text-center leading-relaxed">Create prediction markets directly on Twitter. Automatically showing trading UI in tweets.</p>
                <div className="mt-4 p-3 bg-slate-800/50 rounded-lg border border-green-400/30">
                  <p className="text-sm text-green-300 text-center">
                    <span className="font-bold">Simply post something like this:</span> "prove-me-wrong.com Bitcoin will hit $100k by end of year"
                  </p>
                </div>
                <div className="absolute -top-2 -left-2 w-4 h-4 bg-green-400 rounded-full animate-bounce"></div>
              </div>
            </div>

            <div className="relative group">
              <div className="bg-gradient-to-br from-purple-500/20 to-pink-600/20 rounded-3xl p-8 border border-purple-400/30 transform rotate-2 group-hover:rotate-0 transition-all duration-500 hover:scale-110">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500/30 to-pink-600/30 rounded-3xl flex items-center justify-center mx-auto mb-6 transform -rotate-2 group-hover:rotate-0 transition-transform duration-500">
                  <span className="text-5xl">🤖</span>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-purple-400 text-center">AI Resolution</h3>
                <p className="text-slate-300 text-center leading-relaxed">Our AI analyzes evidence and determines who was right</p>
                <div className="absolute -bottom-2 -right-2 w-4 h-4 bg-purple-400 rounded-full animate-pulse"></div>
              </div>
            </div>
          </div>
        </section>

        {/* Market Stats & Liquidity - Looney Tunes Layout */}
        <section className="slide-up">
          <div className="grid lg:grid-cols-5 gap-8 max-w-7xl mx-auto">
            {/* Market Stats - Takes 2 columns */}
            <div className="lg:col-span-2">
              <div className="relative group">
                <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-3xl p-8 border border-slate-600/30 transform rotate-1 group-hover:rotate-0 transition-all duration-500 hover:scale-105">
                  <div className="flex items-center gap-3 mb-8">
                    <span className="text-3xl">📊</span>
                    <h3 className="text-3xl font-bold text-center">Platform Stats</h3>
                    <span className="text-3xl">📈</span>
                  </div>
                  <div className="space-y-6">
                    <div className="flex items-center justify-between p-6 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-2xl border border-green-400/30 transform hover:scale-105 transition-transform duration-300">
                      <div className="flex items-center gap-4">
                        <div className="w-4 h-4 bg-green-400 rounded-full animate-pulse"></div>
                        <span className="font-semibold">Active Markets</span>
                      </div>
                      <span className="text-3xl font-bold text-green-400">1,247</span>
                    </div>

                    <div className="flex items-center justify-between p-6 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl border border-blue-400/30 transform hover:scale-105 transition-transform duration-300">
                      <div className="flex items-center gap-4">
                        <div className="w-4 h-4 bg-blue-400 rounded-full animate-pulse"></div>
                        <span className="font-semibold">Total Volume</span>
                      </div>
                      <span className="text-3xl font-bold text-blue-400">$2.45M</span>
                    </div>

                    <div className="flex items-center justify-between p-6 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl border border-purple-400/30 transform hover:scale-105 transition-transform duration-300">
                      <div className="flex items-center gap-4">
                        <div className="w-4 h-4 bg-purple-400 rounded-full animate-pulse"></div>
                        <span className="font-semibold">Predictors</span>
                      </div>
                      <span className="text-3xl font-bold text-purple-400">8,472</span>
                    </div>

                    <div className="flex items-center justify-between p-6 bg-gradient-to-r from-orange-500/20 to-red-500/20 rounded-2xl border border-orange-400/30 transform hover:scale-105 transition-transform duration-300">
                      <div className="flex items-center gap-4">
                        <div className="w-4 h-4 bg-orange-400 rounded-full animate-pulse"></div>
                        <span className="font-semibold">AI Accuracy</span>
                      </div>
                      <span className="text-3xl font-bold text-orange-400">94.2%</span>
                    </div>

                    {isConnected && (
                      <div className="p-6 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-2xl border border-yellow-400/30 transform hover:scale-105 transition-transform duration-300">
                        <div className="text-center">
                          <div className="text-sm text-yellow-400 mb-2 font-bold">🎉 Your Winnings</div>
                          <div className="text-4xl font-bold text-yellow-400">$1,234</div>
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="absolute -top-3 -right-3 w-6 h-6 bg-yellow-400 rounded-full animate-bounce"></div>
                </div>
              </div>
            </div>

            {/* Liquidity Interface - Takes 3 columns */}
            <div className="lg:col-span-3">
              <div className="relative group">
                <div className="bg-gradient-to-br from-green-500/20 to-emerald-600/20 rounded-3xl p-8 border border-green-400/30 transform -rotate-1 group-hover:rotate-0 transition-all duration-500 hover:scale-105 relative overflow-hidden">
                  {/* Bullish background elements */}
                  <div className="absolute top-0 right-0 w-40 h-40 bg-green-500/10 rounded-full blur-3xl"></div>
                  <div className="absolute bottom-0 left-0 w-32 h-32 bg-yellow-500/10 rounded-full blur-2xl"></div>

                  <div className="relative z-10">
                    <div className="flex items-center gap-4 mb-8">
                      <span className="text-5xl">🚀</span>
                      <h3 className="text-4xl font-bold">Earn Massive Yields</h3>
                      <span className="text-5xl">💎</span>
                    </div>

                    <div className="space-y-6">
                      <div className="flex justify-between items-center p-6 bg-gradient-to-r from-green-500/30 to-blue-500/30 rounded-2xl border border-green-400/40 transform hover:scale-105 transition-transform duration-300">
                        <div className="flex items-center gap-4">
                          <span className="text-3xl">💰</span>
                          <div>
                            <div className="text-slate-300 text-sm font-bold">Total Value Locked</div>
                            <div className="text-3xl font-bold text-green-400">$4.2M</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-green-400 text-lg font-bold">🔥 HOT</div>
                          <div className="text-yellow-400 text-sm">Trending Up</div>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="flex gap-4">
                          <Input
                            type="number"
                            placeholder="Enter amount to deposit"
                            value={depositAmount}
                            onChange={(e) => setDepositAmount(e.target.value)}
                            className="bg-slate-800/50 border-slate-700 rounded-2xl text-lg p-4 flex-1"
                          />
                          <Button className="bg-slate-700 hover:bg-slate-600 text-white px-6 rounded-2xl font-bold">Max</Button>
                        </div>

                        {depositAmount && (
                          <div className="grid grid-cols-2 gap-4">
                            <div className="p-6 bg-gradient-to-r from-green-500/30 to-emerald-500/30 rounded-2xl border border-green-400/40 text-center transform hover:scale-110 transition-transform duration-300">
                              <div className="text-3xl mb-3">📈</div>
                              <div className="text-sm text-green-400 mb-2 font-bold">Estimated APY</div>
                              <div className="text-4xl font-bold text-green-400">
                                {((Number.parseFloat(depositAmount) / 1000) * 25 + 45).toFixed(1)}%
                              </div>
                              <div className="text-xs text-green-300 mt-2 font-bold">🔥 INSANE RETURNS</div>
                            </div>
                            <div className="p-6 bg-gradient-to-r from-blue-500/30 to-purple-500/30 rounded-2xl border border-blue-400/40 text-center transform hover:scale-110 transition-transform duration-300">
                              <div className="text-3xl mb-3">🎯</div>
                              <div className="text-sm text-blue-400 mb-2 font-bold">Pool Share</div>
                              <div className="text-4xl font-bold text-blue-400">
                                {((Number.parseFloat(depositAmount) / 4200000) * 100).toFixed(3)}%
                              </div>
                              <div className="text-xs text-blue-300 mt-2 font-bold">💎 DIAMOND HANDS</div>
                            </div>
                          </div>
                        )}

                        <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-2xl p-6 border border-yellow-400/30 transform hover:scale-105 transition-transform duration-300">
                          <div className="flex items-center gap-3 text-yellow-400 font-bold text-lg">
                            <span className="text-2xl">⚡</span>
                            <span>Limited Time: 2x Rewards for Early LPs!</span>
                            <span className="text-2xl">⚡</span>
                          </div>
                        </div>

                        <div className="w-full bg-gradient-to-r from-slate-600 to-slate-700 text-white py-6 rounded-2xl text-2xl font-bold text-center border-2 border-dashed border-slate-500">
                          🚧 Coming Soon
                        </div>
                        <p className="text-sm text-slate-400 text-center mt-4">
                          Liquidity providers fund markets and earn a cut of winnings
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="absolute -top-4 -left-4 w-8 h-8 bg-yellow-400 rounded-full animate-bounce"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Recent Markets - Looney Tunes Grid */}
        <section className="slide-up">
          <div className="text-center mb-16">
            <div className="relative inline-block">
              <h2 className="text-6xl font-black mb-4">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-500 to-pink-600 transform rotate-1 inline-block">
                  Recent
                </span>
                <span className="text-white block">Markets</span>
              </h2>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-400 rounded-full animate-bounce"></div>
              <div className="absolute -bottom-2 -left-2 w-4 h-4 bg-purple-400 rounded-full animate-pulse"></div>
            </div>
            <p className="text-2xl text-slate-400">See what people are predicting right now</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
            {[
              {
                title: "Bitcoin will hit $100k by end of 2024",
                author: "@crypto_bull",
                volume: "$45.2k",
                outcome: "Pending",
                timeLeft: "2 days",
                rotation: "rotate-2"
              },
              {
                title: "Tesla stock will drop 20% this month",
                author: "@stock_bear",
                volume: "$23.1k",
                outcome: "YES",
                timeLeft: "Resolved",
                rotation: "-rotate-1"
              },
              {
                title: "ChatGPT will pass the bar exam",
                author: "@ai_optimist",
                volume: "$67.8k",
                outcome: "NO",
                timeLeft: "Resolved",
                rotation: "rotate-3"
              },
              {
                title: "SpaceX will land on Mars in 2025",
                author: "@space_enthusiast",
                volume: "$12.4k",
                outcome: "Pending",
                timeLeft: "5 months",
                rotation: "-rotate-2"
              },
              {
                title: "Apple will release AR glasses this year",
                author: "@tech_analyst",
                volume: "$89.3k",
                outcome: "Pending",
                timeLeft: "3 months",
                rotation: "rotate-1"
              },
              {
                title: "Ethereum will flip Bitcoin market cap",
                author: "@defi_maxi",
                volume: "$156.7k",
                outcome: "Pending",
                timeLeft: "1 year",
                rotation: "-rotate-3"
              }
            ].map((market, index) => (
              <div
                key={index}
                className={`group relative ${market.rotation} hover:rotate-0 transition-all duration-500 hover:scale-110`}
              >
                <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-3xl p-6 border border-slate-600/30">
                  <h3 className="font-bold text-xl mb-4 line-clamp-2 text-center">{market.title}</h3>
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-blue-400 text-sm font-bold">{market.author}</span>
                    <span className="text-slate-400 text-sm">{market.timeLeft}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-green-400 font-bold text-lg">{market.volume}</span>
                    <span className={`px-4 py-2 rounded-full text-sm font-bold ${market.outcome === "YES" ? "bg-green-500/30 text-green-400 border border-green-400/30" :
                      market.outcome === "NO" ? "bg-red-500/30 text-red-400 border border-red-400/30" :
                        "bg-blue-500/30 text-blue-400 border border-blue-400/30"
                      }`}>
                      {market.outcome}
                    </span>
                  </div>
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-yellow-400 rounded-full animate-pulse"></div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Leaderboard - Looney Tunes Style */}
        <section className="slide-up">
          <div className="text-center mb-16">
            <div className="relative inline-block">
              <h2 className="text-6xl font-black mb-4">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 transform -rotate-1 inline-block">
                  Top
                </span>
                <span className="text-white block">Predictors</span>
              </h2>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-400 rounded-full animate-bounce"></div>
              <div className="absolute -bottom-2 -left-2 w-4 h-4 bg-orange-400 rounded-full animate-pulse"></div>
            </div>
          </div>

          <div className="max-w-5xl mx-auto">
            <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-3xl p-8 border border-slate-600/30 transform hover:scale-105 transition-transform duration-500">
              <div className="space-y-4">
                {[
                  { rank: 1, name: "vitalik.eth", markets: "47", accuracy: "89%", earned: "$15,420", rotation: "rotate-1" },
                  { rank: 2, name: "whale_hunter", markets: "32", accuracy: "84%", earned: "$8,750", rotation: "-rotate-1" },
                  { rank: 3, name: "defi_master", markets: "28", accuracy: "82%", earned: "$6,200", rotation: "rotate-2" },
                  { rank: 4, name: "crypto_ninja", markets: "41", accuracy: "78%", earned: "$4,100", rotation: "-rotate-2" },
                  { rank: 5, name: "moon_farmer", markets: "23", accuracy: "91%", earned: "$3,800", rotation: "rotate-1" },
                ].map((player, index) => (
                  <div
                    key={player.rank}
                    className={`group ${player.rotation} hover:rotate-0 transition-all duration-500 hover:scale-105 p-6 rounded-2xl ${player.rank === 1
                      ? "bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-400/30"
                      : "bg-slate-800/30 hover:bg-slate-800/50 border border-slate-600/30"
                      }`}
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-6">
                        <div className="text-4xl">{player.rank === 1 ? "👑" : `#${player.rank}`}</div>
                        <div>
                          <div className="font-bold text-xl">{player.name}</div>
                          <div className="text-slate-400 text-sm font-semibold">{player.markets} markets • {player.accuracy} accuracy</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-2xl text-blue-400">{player.earned}</div>
                        <div className="text-green-400 text-sm font-bold">Total winnings</div>
                      </div>
                    </div>
                    <div className="absolute -top-2 -right-2 w-4 h-4 bg-yellow-400 rounded-full animate-pulse"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section - Looney Tunes Style */}
        <section className="text-center py-16 slide-up">
          <div className="relative group">
            <div className="bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-3xl p-12 border border-blue-400/30 max-w-5xl mx-auto transform rotate-1 group-hover:rotate-0 transition-all duration-500 hover:scale-105">
              <div className="relative z-10">
                <div className="flex items-center justify-center gap-4 mb-8">
                  <span className="text-5xl">🎯</span>
                  <h2 className="text-5xl font-black">Ready to Prove Them Wrong?</h2>
                  <span className="text-5xl">🚀</span>
                </div>
                <p className="text-2xl text-slate-300 mb-8 leading-relaxed">
                  Join thousands of predictors making markets on Twitter.
                  <span className="text-yellow-400 font-bold"> Install the extension and start creating prediction markets today.</span>
                </p>
                <div className="flex flex-col sm:flex-row gap-6 justify-center">
                  <Button
                    onClick={() => window.open("/extension/dist.zip", "_blank")}
                    className="bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-black px-10 py-6 rounded-2xl font-bold shadow-lg shadow-yellow-500/25 hover:shadow-yellow-500/40 transition-all duration-300 text-xl transform hover:scale-105"
                  >
                    🚀 Get Extension Now
                  </Button>
                  <Button
                    onClick={() => window.open("https://twitter.com/RealWooblay", "_blank")}
                    className="bg-slate-800 hover:bg-slate-700 text-white px-10 py-6 rounded-2xl font-bold transition-all duration-300 text-xl border-2 border-slate-600 hover:border-slate-500 transform hover:scale-105"
                  >
                    🐦 Browse Markets
                  </Button>
                </div>
              </div>
              <div className="absolute -top-4 -right-4 w-8 h-8 bg-yellow-400 rounded-full animate-bounce"></div>
              <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-blue-400 rounded-full animate-pulse"></div>
            </div>
          </div>
        </section>
      </div>

      <style jsx>{`
        .slide-up {
          animation: slideUp 0.8s ease-out;
        }
        
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .creative-card {
          background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
          border: 1px solid rgba(59, 130, 246, 0.1);
          backdrop-filter: blur(10px);
        }
        
        .creative-card-accent {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
          border: 1px solid rgba(59, 130, 246, 0.2);
          backdrop-filter: blur(10px);
        }
        
        .rotate-card {
          transform: rotate(-2deg);
        }
        
        .rotate-card-reverse {
          transform: rotate(2deg);
        }
        
        .float {
          animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  )
}
