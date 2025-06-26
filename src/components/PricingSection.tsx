import React from 'react'
import { Check } from 'lucide-react'

export const PricingSection = () => {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'For individuals getting started with PDF collaboration',
      features: [
        '5 PDFs per month',
        'Basic editing tools',
        'Up to 3 collaborators',
        '100MB storage',
        'Email support',
      ],
      buttonText: 'Get Started',
      buttonVariant: 'outlined',
    },
    {
      name: 'Pro',
      price: '$12',
      period: 'per user / month',
      description: 'For professionals who need more power and storage',
      features: [
        'Unlimited PDFs',
        'Advanced editing tools',
        'Up to 20 collaborators',
        '10GB storage',
        'Priority support',
        'Digital signatures',
        'Custom branding',
      ],
      buttonText: 'Start Free Trial',
      buttonVariant: 'primary',
      popular: true,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: 'tailored pricing',
      description: 'For organizations with advanced security needs',
      features: [
        'Everything in Pro',
        'Unlimited collaborators',
        'Unlimited storage',
        '24/7 dedicated support',
        'Advanced security controls',
        'API access',
        'SSO integration',
      ],
      buttonText: 'Contact Sales',
      buttonVariant: 'outlined',
    },
  ]

  return (
    <section id="pricing" className="py-16 bg-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
            Simple, Transparent Pricing
          </h2>
          <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
            Choose the plan that's right for you and your team
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`bg-white rounded-lg shadow-md overflow-hidden ${plan.popular ? 'ring-2 ring-blue-600 relative' : ''}`}
            >
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-bl-lg">
                  Most Popular
                </div>
              )}
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  {plan.name}
                </h3>
                <div className="mt-4 flex items-baseline">
                  <span className="text-4xl font-extrabold text-gray-900">
                    {plan.price}
                  </span>
                  <span className="ml-1 text-xl font-semibold text-gray-500">
                    /{plan.period}
                  </span>
                </div>
                <p className="mt-4 text-gray-600">{plan.description}</p>
              </div>
              <div className="px-6 pb-6">
                <ul className="mt-6 space-y-4">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <Check className="h-5 w-5 text-green-500 shrink-0 mr-2" />
                      <span className="text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                <div className="mt-8">
                  <a
                    href="/auth/register"
                    className={`w-full flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md ${plan.buttonVariant === 'primary' ? 'text-white bg-blue-600 hover:bg-blue-700' : 'text-blue-600 bg-white border-blue-600 hover:bg-blue-50'}`}
                  >
                    {plan.buttonText}
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-12 text-center">
          <p className="text-gray-600">
            All plans include a 14-day free trial. No credit card required.
          </p>
        </div>
      </div>
    </section>
  )
}