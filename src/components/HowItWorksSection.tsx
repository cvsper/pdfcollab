import React from 'react'
import { Upload, Edit3, Share2, ArrowRight } from 'lucide-react'

export const HowItWorksSection = () => {
  const steps = [
    {
      icon: <Upload className="h-10 w-10 text-blue-600" />,
      title: 'Upload Your PDF',
      description:
        'Upload your PDF document from your computer or cloud storage.',
    },
    {
      icon: <Edit3 className="h-10 w-10 text-blue-600" />,
      title: 'Edit & Annotate',
      description: 'Make changes, add comments, and annotate your document.',
    },
    {
      icon: <Share2 className="h-10 w-10 text-blue-600" />,
      title: 'Collaborate & Share',
      description:
        'Invite team members to collaborate and share the document securely.',
    },
  ]

  return (
    <section id="how-it-works" className="py-16 bg-blue-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
            How PDFCollab Works
          </h2>
          <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
            Get started in minutes with our simple three-step process
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="bg-white p-8 rounded-lg shadow-md text-center h-full">
                <div className="mx-auto bg-blue-100 p-4 rounded-full inline-flex items-center justify-center mb-4">
                  {step.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2">
                  <ArrowRight className="h-8 w-8 text-blue-400" />
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="mt-12 text-center">
          <a
            href="/auth/register"
            className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Get Started Now
          </a>
        </div>
      </div>
    </section>
  )
}