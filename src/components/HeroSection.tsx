import React from 'react'
import { FileTextIcon, UsersIcon, CheckCircleIcon } from 'lucide-react'

export const HeroSection = () => {
  return (
    <section className="bg-gradient-to-b from-white to-blue-50 py-16 md:py-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="lg:flex lg:items-center lg:justify-between">
          <div className="lg:w-1/2 mb-8 lg:mb-0">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-gray-900 leading-tight">
              Collaborate on PDFs{' '}
              <span className="text-blue-600">in real-time</span>
            </h1>
            <p className="mt-4 text-xl text-gray-600 max-w-2xl">
              Edit, annotate, and collaborate on PDF documents with your team.
              PDFCollab makes working with PDFs simple and efficient.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
              <a
                href="/auth/register"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Try for free
              </a>
              <a
                href="#how-it-works"
                className="inline-flex items-center justify-center px-5 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Watch demo
              </a>
            </div>
            <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="flex items-center">
                <CheckCircleIcon className="h-5 w-5 text-blue-600 mr-2" />
                <span className="text-gray-600">No installation</span>
              </div>
              <div className="flex items-center">
                <CheckCircleIcon className="h-5 w-5 text-blue-600 mr-2" />
                <span className="text-gray-600">Real-time editing</span>
              </div>
              <div className="flex items-center">
                <CheckCircleIcon className="h-5 w-5 text-blue-600 mr-2" />
                <span className="text-gray-600">Free to start</span>
              </div>
            </div>
          </div>
          <div className="lg:w-1/2 relative">
            <div className="rounded-lg shadow-xl overflow-hidden bg-white">
              <img
                src="https://images.unsplash.com/photo-1586282391129-76a6df230234?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
                alt="PDF collaboration interface"
                className="w-full object-cover"
              />
              <div className="absolute -bottom-6 -right-6 bg-blue-600 rounded-full p-4 shadow-lg">
                <FileTextIcon className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}