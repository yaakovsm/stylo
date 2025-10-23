import React from 'react'

const About: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto py-12">
      <h1 className="text-3xl md:text-4xl font-semibold tracking-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>About Style Sync</h1>
      <p className="text-muted-foreground mb-6">
        Style Sync helps you translate intent into polished looks with AI-assisted recommendations, curated color palettes, and quick visual validation.
      </p>
      <p className="text-muted-foreground">
        Built with care for clarity, speed, and taste. We never change or expose your API configuration from this page.
      </p>
    </div>
  )
}

export default About

