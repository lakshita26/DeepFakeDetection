"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Shield, Upload, BarChart3, History, Info } from "lucide-react"
import Link from "next/link"
import Image from "next/image"

interface NavigationProps {
  currentSection: string
  onSectionChange: (section: "home" | "upload" | "results" | "history" | "about") => void
}

export function Navigation({ currentSection, onSectionChange }: NavigationProps) {
  const navItems = [
    { id: "home", label: "Home", icon: Shield },
    { id: "upload", label: "Analyze", icon: Upload },
    { id: "results", label: "Results", icon: BarChart3 },
    { id: "history", label: "History", icon: History },
    { id: "about", label: "About", icon: Info },
  ] as const

  return (
    <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-2">
            <Image src="/logo.png" alt="logo" width={40} height={40} />
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Darpana
            </span>
          </motion.div>

          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-2">
              <Link href="/login">
                <Button variant="ghost" size="sm">Login</Button>
              </Link>
              <Link href="/signup">
                <Button variant="default" size="sm">Sign Up</Button>
              </Link>
            </div>
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = currentSection === item.id

              return (
                <Button
                  key={item.id}
                  variant={isActive ? "default" : "ghost"}
                  size="sm"
                  onClick={() => onSectionChange(item.id)}
                  className="relative"
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {item.label}
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 bg-primary rounded-md -z-10"
                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                </Button>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
