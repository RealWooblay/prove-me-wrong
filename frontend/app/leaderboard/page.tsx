"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Search, Download, Crown, TrendingUp, TrendingDown } from "lucide-react"

const leaderboardData = [
  {
    rank: 1,
    address: "vitalik.eth",
    deposited: 15420000,
    earnings: 285000,
    roi: 18.5,
    change24h: 2.3,
  },
  {
    rank: 2,
    address: "0x1234...5678",
    deposited: 8750000,
    earnings: 162000,
    roi: 18.5,
    change24h: -1.2,
  },
  {
    rank: 3,
    address: "whale.eth",
    deposited: 6200000,
    earnings: 114000,
    roi: 18.4,
    change24h: 0.8,
  },
  {
    rank: 4,
    address: "0xabcd...efgh",
    deposited: 4100000,
    earnings: 75000,
    roi: 18.3,
    change24h: 1.5,
  },
  {
    rank: 5,
    address: "defi.eth",
    deposited: 3800000,
    earnings: 69000,
    roi: 18.2,
    change24h: -0.5,
  },
]

export default function Leaderboard() {
  const [searchTerm, setSearchTerm] = useState("")
  const [activeFilter, setActiveFilter] = useState("all-time")

  const filters = [
    { id: "all-time", label: "All-time" },
    { id: "30d", label: "30 d" },
    { id: "24h", label: "24 h" },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-20">
      <div className="container mx-auto px-4">
        <div className="animate-slide-up">
          <h1 className="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-white to-blue-400 bg-clip-text text-transparent">
            Liquidity Leaderboard
          </h1>

          <Card className="glass-card dark:glass-card mb-8">
            <CardHeader>
              <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
                <div className="flex space-x-2">
                  {filters.map((filter) => (
                    <Button
                      key={filter.id}
                      variant={activeFilter === filter.id ? "default" : "outline"}
                      onClick={() => setActiveFilter(filter.id)}
                      className="hover:animate-bounce-micro"
                    >
                      {filter.label}
                    </Button>
                  ))}
                </div>

                <div className="flex space-x-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search address or ENS..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 bg-white/5 border-white/10"
                    />
                  </div>
                  <Button variant="outline" className="hover:animate-bounce-micro bg-transparent">
                    <Download className="h-4 w-4 mr-2" />
                    CSV
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="sticky top-0 bg-slate-800/80 backdrop-blur-sm">
                    <tr className="border-b border-white/10">
                      <th className="text-left py-4 px-4 font-semibold">Rank</th>
                      <th className="text-left py-4 px-4 font-semibold">Address</th>
                      <th className="text-right py-4 px-4 font-semibold">Total Deposited</th>
                      <th className="text-right py-4 px-4 font-semibold">Earnings</th>
                      <th className="text-right py-4 px-4 font-semibold">ROI %</th>
                      <th className="text-right py-4 px-4 font-semibold">24h Δ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboardData.map((user, index) => (
                      <tr
                        key={user.rank}
                        className="border-b border-white/5 hover:bg-white/5 transition-colors animate-slide-up"
                        style={{ animationDelay: `${index * 0.1}s` }}
                      >
                        <td className="py-4 px-4">
                          <div className="flex items-center">
                            {user.rank === 1 && <Crown className="h-5 w-5 text-yellow-400 mr-2 animate-bounce" />}
                            <Badge
                              variant={user.rank <= 3 ? "default" : "secondary"}
                              className={`
                                ${user.rank === 1 ? "neon-glow bg-yellow-500/20 text-yellow-400" : ""}
                                ${user.rank === 2 ? "bg-gray-500/20 text-gray-300" : ""}
                                ${user.rank === 3 ? "bg-orange-500/20 text-orange-400" : ""}
                              `}
                            >
                              #{user.rank}
                            </Badge>
                          </div>
                        </td>
                        <td className="py-4 px-4 font-mono text-blue-400">{user.address}</td>
                        <td className="py-4 px-4 text-right font-semibold">${user.deposited.toLocaleString()}</td>
                        <td className="py-4 px-4 text-right text-green-400 font-semibold">
                          ${user.earnings.toLocaleString()}
                        </td>
                        <td className="py-4 px-4 text-right font-semibold">{user.roi}%</td>
                        <td className="py-4 px-4 text-right">
                          <div
                            className={`flex items-center justify-end ${
                              user.change24h > 0 ? "text-green-400" : "text-red-400"
                            }`}
                          >
                            {user.change24h > 0 ? (
                              <TrendingUp className="h-4 w-4 mr-1" />
                            ) : (
                              <TrendingDown className="h-4 w-4 mr-1" />
                            )}
                            {Math.abs(user.change24h)}%
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
