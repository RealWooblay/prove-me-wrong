"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Copy, Wallet, Twitter, TrendingUp } from "lucide-react"
import Link from "next/link"

export default function HowTo() {
  const sampleTweetUrl =
    "https://twitter.com/compose/tweet?text=Check%20out%20this%20amazing%20DeFi%20opportunity%20on%20LiquidityHub!%20%23DeFi%20%23Web3"

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-20">
      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Left Column - Guide */}
          <div className="animate-slide-up">
            <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-white to-blue-400 bg-clip-text text-transparent">
              How to Get Started
            </h1>

            <div className="space-y-8">
              <Card className="glass-card dark:glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center text-xl">
                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-sm font-bold mr-3">
                      1
                    </div>
                    Connect Wallet & Deposit LP
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300 mb-4">
                    Connect your Web3 wallet and deposit liquidity to start earning fees from trades.
                  </p>
                  <Link href="/">
                    <Button className="gradient-cta hover:animate-bounce-micro">
                      <Wallet className="mr-2 h-4 w-4" />
                      Go to Dashboard
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              <Card className="glass-card dark:glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center text-xl">
                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-sm font-bold mr-3">
                      2
                    </div>
                    Share on Twitter
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300 mb-4">
                    Post a tweet that embeds a market. Paste the sample URL below into Twitter's composer:
                  </p>
                  <div className="bg-slate-800/50 rounded-lg p-4 mb-4">
                    <code className="text-sm text-blue-400 break-all">{sampleTweetUrl}</code>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => copyToClipboard(sampleTweetUrl)}
                      className="hover:animate-bounce-micro"
                    >
                      <Copy className="mr-2 h-4 w-4" />
                      Copy URL
                    </Button>
                    <Button
                      className="gradient-cta hover:animate-bounce-micro"
                      onClick={() => window.open(sampleTweetUrl, "_blank")}
                    >
                      <Twitter className="mr-2 h-4 w-4" />
                      Tweet Now
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-card dark:glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center text-xl">
                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-sm font-bold mr-3">
                      3
                    </div>
                    Earn Rewards
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300 mb-4">
                    Watch your earnings grow as traders use your liquidity. Track your performance on the leaderboard.
                  </p>
                  <Link href="/leaderboard">
                    <Button variant="outline" className="hover:animate-bounce-micro bg-transparent">
                      <TrendingUp className="mr-2 h-4 w-4" />
                      View Leaderboard
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Right Column - Interactive Demo */}
          <div className="animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <Card className="glass-card dark:glass-card sticky top-24">
              <CardHeader>
                <CardTitle className="text-2xl">Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-500/10 rounded-lg">
                    <div className="text-2xl font-bold text-blue-400">18.5%</div>
                    <div className="text-sm text-gray-400">Current APY</div>
                  </div>
                  <div className="text-center p-4 bg-green-500/10 rounded-lg">
                    <div className="text-2xl font-bold text-green-400">$2.4M</div>
                    <div className="text-sm text-gray-400">Total TVL</div>
                  </div>
                  <div className="text-center p-4 bg-purple-500/10 rounded-lg">
                    <div className="text-2xl font-bold text-purple-400">1,247</div>
                    <div className="text-sm text-gray-400">Active Users</div>
                  </div>
                  <div className="text-center p-4 bg-yellow-500/10 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-400">$125K</div>
                    <div className="text-sm text-gray-400">Daily Volume</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Risk Levels</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Conservative</span>
                      <Badge variant="secondary" className="bg-green-500/20 text-green-400">
                        8-12% APY
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Moderate</span>
                      <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-400">
                        12-18% APY
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Aggressive</span>
                      <Badge variant="secondary" className="bg-red-500/20 text-red-400">
                        18%+ APY
                      </Badge>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <h3 className="text-lg font-semibold mb-4">Calculate Potential Earnings</h3>
                  <div className="space-y-3">
                    <Input
                      type="number"
                      placeholder="Enter deposit amount (ETH)"
                      className="bg-white/5 border-white/10"
                    />
                    <div className="text-center p-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg">
                      <div className="text-lg font-semibold text-blue-400">Estimated Monthly: $0</div>
                      <div className="text-sm text-gray-400">Based on current 18.5% APY</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
