import React, { useState } from 'react'
import { Menu, X, ChevronDown } from 'lucide-react'

export const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl font-bold text-blue-600">
                PDFCollab
              </span>
            </div>
            <nav className="hidden md:ml-10 md:flex md:space-x-8">
              <a
                href="#features"
                className="text-gray-600 hover:text-blue-600 px-3 py-2 text-sm font-medium"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                className="text-gray-600 hover:text-blue-600 px-3 py-2 text-sm font-medium"
              >
                How It Works
              </a>
              <a
                href="#testimonials"
                className="text-gray-600 hover:text-blue-600 px-3 py-2 text-sm font-medium"
              >
                Testimonials
              </a>
              <div className="relative group">
                <button className="flex items-center text-gray-600 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                  Solutions <ChevronDown className="ml-1 h-4 w-4" />
                </button>
                <div className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 hidden group-hover:block">
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    For Teams
                  </a>
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    For Education
                  </a>
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    For Enterprise
                  </a>
                </div>
              </div>
              <a
                href="#pricing"
                className="text-gray-600 hover:text-blue-600 px-3 py-2 text-sm font-medium"
              >
                Pricing
              </a>
            </nav>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <a
              href="/auth/login"
              className="text-gray-600 hover:text-blue-600 px-3 py-2 text-sm font-medium"
            >
              Login
            </a>
            <a
              href="/auth/register"
              className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium"
            >
              Sign Up Free
            </a>
          </div>
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-600 hover:text-blue-600 hover:bg-gray-100 focus:outline-none"
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>
      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-white shadow-md">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <a
              href="#features"
              className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-blue-600"
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-blue-600"
            >
              How It Works
            </a>
            <a
              href="#testimonials"
              className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-blue-600"
            >
              Testimonials
            </a>
            <a
              href="#pricing"
              className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-blue-600"
            >
              Pricing
            </a>
            <a
              href="/auth/login"
              className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-blue-600"
            >
              Login
            </a>
            <a
              href="/auth/register"
              className="block px-3 py-2 text-base font-medium bg-blue-600 text-white rounded-md"
            >
              Sign Up Free
            </a>
          </div>
        </div>
      )}
    </header>
  )
}