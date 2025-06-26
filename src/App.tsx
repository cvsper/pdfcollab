import React from 'react'
import { Header } from './components/Header'
import { HeroSection } from './components/HeroSection'
import { FeaturesSection } from './components/FeaturesSection'
import { HowItWorksSection } from './components/HowItWorksSection'
import { TestimonialsSection } from './components/TestimonialsSection'
import { PricingSection } from './components/PricingSection'
import { Footer } from './components/Footer'

export function App() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
        <TestimonialsSection />
        <PricingSection />
      </main>
      <Footer />
    </div>
  )
}