import React from 'react'
import {
  FileTextIcon,
  UsersIcon,
  MessageSquareIcon,
  PenToolIcon,
  LockIcon,
  CloudIcon,
} from 'lucide-react'

export const FeaturesSection = () => {
  const features = [
    {
      icon: <FileTextIcon className="h-8 w-8 text-blue-600" />,
      title: 'PDF Editing',
      description:
        'Edit text, images, and pages in PDFs without the need for specialized software.',
    },
    {
      icon: <UsersIcon className="h-8 w-8 text-blue-600" />,
      title: 'Real-time Collaboration',
      description:
        'Work together with your team simultaneously on the same document.',
    },
    {
      icon: <MessageSquareIcon className="h-8 w-8 text-blue-600" />,
      title: 'Comments & Annotations',
      description:
        'Add notes, highlights, and comments directly on your PDF documents.',
    },
    {
      icon: <PenToolIcon className="h-8 w-8 text-blue-600" />,
      title: 'Digital Signatures',
      description:
        'Sign documents electronically and request signatures from others.',
    },
    {
      icon: <LockIcon className="h-8 w-8 text-blue-600" />,
      title: 'Secure Document Sharing',
      description:
        'Control access with password protection and permission settings.',
    },
    {
      icon: <CloudIcon className="h-8 w-8 text-blue-600" />,
      title: 'Cloud Storage',
      description:
        'Access your PDFs from anywhere, on any device with cloud storage.',
    },
  ]

  return (
    <section id="features" className="py-16 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
            Powerful PDF Collaboration Tools
          </h2>
          <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
            Everything you need to work with PDFs in one simple platform
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300"
            >
              <div className="mb-4 bg-blue-50 p-3 rounded-full inline-block">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}