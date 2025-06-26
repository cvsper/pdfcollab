import React from 'react'
import { Star } from 'lucide-react'

export const TestimonialsSection = () => {
  const testimonials = [
    {
      content:
        'PDFCollab has revolutionized how our team works with documents. The real-time collaboration feature has cut our review time in half.',
      author: 'Sarah Johnson',
      role: 'Project Manager, TechCorp',
      avatar: 'https://randomuser.me/api/portraits/women/32.jpg',
    },
    {
      content:
        "As a legal firm, we deal with countless documents daily. PDFCollab's annotation and signature features have streamlined our workflow tremendously.",
      author: 'Michael Chen',
      role: 'Attorney, Legal Solutions',
      avatar: 'https://randomuser.me/api/portraits/men/45.jpg',
    },
    {
      content:
        "The ease of use and powerful features make PDFCollab stand out from other PDF tools. It's become an essential part of our document management system.",
      author: 'Emily Rodriguez',
      role: 'Director of Operations, Innovate Inc.',
      avatar: 'https://randomuser.me/api/portraits/women/68.jpg',
    },
  ]

  return (
    <section id="testimonials" className="py-16 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
            What Our Users Say
          </h2>
          <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
            Join thousands of satisfied users who've transformed their PDF
            workflow
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="bg-gray-50 p-6 rounded-lg border border-gray-200"
            >
              <div className="flex mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className="h-5 w-5 text-yellow-400 fill-current"
                  />
                ))}
              </div>
              <p className="text-gray-600 mb-6 italic">
                "{testimonial.content}"
              </p>
              <div className="flex items-center">
                <img
                  src={testimonial.avatar}
                  alt={testimonial.author}
                  className="h-10 w-10 rounded-full mr-3"
                />
                <div>
                  <p className="text-gray-900 font-medium">
                    {testimonial.author}
                  </p>
                  <p className="text-gray-500 text-sm">{testimonial.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-12 bg-blue-600 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold text-white mb-4">
            Ready to transform your PDF workflow?
          </h3>
          <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
            Join over 10,000 teams who trust PDFCollab for their document
            collaboration needs.
          </p>
          <a
            href="/auth/register"
            className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50"
          >
            Start Your Free Trial
          </a>
        </div>
      </div>
    </section>
  )
}