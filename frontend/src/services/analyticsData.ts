import type { SectorSentiment, CompanySentiment, SentimentTimePoint, PolarityData } from '../types/analytics'

export const sectorList = [
  'Banking & Financial Services',
  'Information Technology',
  'Automobile & Auto Ancillary',
  'Energy, Oil & Gas',
  'Pharmaceuticals & Healthcare',
  'Fast Moving Consumer Goods',
  'Metals & Mining',
]

export const companyList = [
  { symbol: 'RELIANCE', name: 'Reliance Industries Ltd', sector: 'Energy, Oil & Gas' },
  { symbol: 'TCS', name: 'Tata Consultancy Services', sector: 'Information Technology' },
  { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd', sector: 'Banking & Financial Services' },
  { symbol: 'INFY', name: 'Infosys Ltd', sector: 'Information Technology' },
  { symbol: 'TATAMOTORS', name: 'Tata Motors Ltd', sector: 'Automobile & Auto Ancillary' },
  { symbol: 'ICICIBANK', name: 'ICICI Bank Ltd', sector: 'Banking & Financial Services' },
  { symbol: 'BHARTIARTL', name: 'Bharti Airtel Ltd', sector: 'Telecom' },
  { symbol: 'ZOMATO', name: 'Zomato Ltd', sector: 'Consumer Tech' },
]

export const sampleTimeframesData: Record<string, SentimentTimePoint[]> = {
  '1D': [
    { date: '09:15', score: 0.58, positive: 12, neutral: 6, negative: 4, volume: 22 },
    { date: '10:30', score: 0.62, positive: 18, neutral: 8, negative: 3, volume: 29 },
    { date: '11:45', score: 0.65, positive: 22, neutral: 9, negative: 4, volume: 35 },
    { date: '13:00', score: 0.61, positive: 19, neutral: 12, negative: 6, volume: 37 },
    { date: '14:15', score: 0.70, positive: 28, neutral: 7, negative: 5, volume: 40 },
    { date: '15:30', score: 0.73, positive: 34, neutral: 8, negative: 4, volume: 46 },
  ],
  '1W': [
    { date: 'Mon', score: 0.54, positive: 85, neutral: 35, negative: 20, volume: 140 },
    { date: 'Tue', score: 0.59, positive: 102, neutral: 40, negative: 18, volume: 160 },
    { date: 'Wed', score: 0.61, positive: 110, neutral: 38, negative: 22, volume: 170 },
    { date: 'Thu', score: 0.68, positive: 135, neutral: 30, negative: 15, volume: 180 },
    { date: 'Fri', score: 0.72, positive: 155, neutral: 32, negative: 13, volume: 200 },
  ],
  '1M': [
    { date: 'Week 1', score: 0.48, positive: 310, neutral: 150, negative: 120, volume: 580 },
    { date: 'Week 2', score: 0.55, positive: 380, neutral: 140, negative: 90, volume: 610 },
    { date: 'Week 3', score: 0.64, positive: 450, neutral: 120, negative: 70, volume: 640 },
    { date: 'Week 4', score: 0.71, positive: 520, neutral: 110, negative: 60, volume: 690 },
  ],
  '1Y': [
    { date: 'Q1', score: 0.45, positive: 1200, neutral: 600, negative: 500, volume: 2300 },
    { date: 'Q2', score: 0.52, positive: 1450, neutral: 580, negative: 420, volume: 2450 },
    { date: 'Q3', score: 0.63, positive: 1800, neutral: 510, negative: 320, volume: 2630 },
    { date: 'Q4', score: 0.74, positive: 2100, neutral: 480, negative: 260, volume: 2840 },
  ],
}

export const sectorSentimentList: SectorSentiment[] = [
  {
    sector: 'Banking & Financial Services',
    score: 0.74,
    momentum: '+4.8%',
    articleCount: 164,
    status: 'Bullish',
    history: sampleTimeframesData['1W'],
  },
  {
    sector: 'Automobile & Auto Ancillary',
    score: 0.69,
    momentum: '+3.1%',
    articleCount: 112,
    status: 'Bullish',
    history: sampleTimeframesData['1W'],
  },
  {
    sector: 'Pharmaceuticals & Healthcare',
    score: 0.63,
    momentum: '+1.9%',
    articleCount: 88,
    status: 'Bullish',
    history: sampleTimeframesData['1W'],
  },
  {
    sector: 'Energy, Oil & Gas',
    score: 0.52,
    momentum: '-0.3%',
    articleCount: 130,
    status: 'Neutral',
    history: sampleTimeframesData['1W'],
  },
  {
    sector: 'Information Technology',
    score: 0.44,
    momentum: '-2.4%',
    articleCount: 145,
    status: 'Cautious',
    history: sampleTimeframesData['1W'],
  },
]

export const companySentimentMap: Record<string, CompanySentiment> = {
  RELIANCE: {
    symbol: 'RELIANCE',
    name: 'Reliance Industries Ltd',
    sector: 'Energy, Oil & Gas',
    score: 0.72,
    delta: '+3.4%',
    newsCount: 42,
    status: 'Bullish',
    keyCatalyst: 'Retail network expansion (120 stores) and resilient petrochemical margins.',
    trend: [
      { date: 'Mon', score: 0.62, positive: 18, neutral: 6, negative: 4, volume: 28 },
      { date: 'Tue', score: 0.65, positive: 20, neutral: 7, negative: 3, volume: 30 },
      { date: 'Wed', score: 0.67, positive: 22, neutral: 6, negative: 4, volume: 32 },
      { date: 'Thu', score: 0.70, positive: 25, neutral: 5, negative: 3, volume: 33 },
      { date: 'Fri', score: 0.72, positive: 28, neutral: 5, negative: 2, volume: 35 },
    ],
  },
  TCS: {
    symbol: 'TCS',
    name: 'Tata Consultancy Services',
    sector: 'Information Technology',
    score: 0.51,
    delta: '-0.8%',
    newsCount: 31,
    status: 'Neutral',
    keyCatalyst: 'Steady BFSI order renewals counterbalanced by cautious discretionary client tech spends.',
    trend: [
      { date: 'Mon', score: 0.55, positive: 10, neutral: 12, negative: 6, volume: 28 },
      { date: 'Tue', score: 0.53, positive: 9, neutral: 11, negative: 7, volume: 27 },
      { date: 'Wed', score: 0.50, positive: 8, neutral: 12, negative: 8, volume: 28 },
      { date: 'Thu', score: 0.52, positive: 10, neutral: 10, negative: 7, volume: 27 },
      { date: 'Fri', score: 0.51, positive: 9, neutral: 12, negative: 6, volume: 27 },
    ],
  },
  HDFCBANK: {
    symbol: 'HDFCBANK',
    name: 'HDFC Bank Ltd',
    sector: 'Banking & Financial Services',
    score: 0.78,
    delta: '+5.2%',
    newsCount: 48,
    status: 'Bullish',
    keyCatalyst: 'Deposit accretion outpacing credit growth; net interest margins stabilizing post-merger.',
    trend: [
      { date: 'Mon', score: 0.68, positive: 22, neutral: 8, negative: 4, volume: 34 },
      { date: 'Tue', score: 0.71, positive: 25, neutral: 7, negative: 3, volume: 35 },
      { date: 'Wed', score: 0.73, positive: 27, neutral: 8, negative: 3, volume: 38 },
      { date: 'Thu', score: 0.76, positive: 30, neutral: 6, negative: 2, volume: 38 },
      { date: 'Fri', score: 0.78, positive: 35, neutral: 5, negative: 2, volume: 42 },
    ],
  },
  INFY: {
    symbol: 'INFY',
    name: 'Infosys Ltd',
    sector: 'Information Technology',
    score: 0.48,
    delta: '-1.5%',
    newsCount: 35,
    status: 'Neutral',
    keyCatalyst: 'Large AI deal wins recognized, but near-term European enterprise budgets remain constrained.',
    trend: [
      { date: 'Mon', score: 0.52, positive: 11, neutral: 10, negative: 7, volume: 28 },
      { date: 'Tue', score: 0.50, positive: 10, neutral: 9, negative: 8, volume: 27 },
      { date: 'Wed', score: 0.47, positive: 9, neutral: 10, negative: 9, volume: 28 },
      { date: 'Thu', score: 0.48, positive: 10, neutral: 9, negative: 8, volume: 27 },
      { date: 'Fri', score: 0.48, positive: 9, neutral: 10, negative: 8, volume: 27 },
    ],
  },
  TATAMOTORS: {
    symbol: 'TATAMOTORS',
    name: 'Tata Motors Ltd',
    sector: 'Automobile & Auto Ancillary',
    score: 0.82,
    delta: '+6.1%',
    newsCount: 39,
    status: 'Bullish',
    keyCatalyst: 'JLR order book robust, domestic EV market share holding dominant above 65%.',
    trend: [
      { date: 'Mon', score: 0.72, positive: 20, neutral: 6, negative: 3, volume: 29 },
      { date: 'Tue', score: 0.75, positive: 23, neutral: 5, negative: 2, volume: 30 },
      { date: 'Wed', score: 0.78, positive: 25, neutral: 6, negative: 2, volume: 33 },
      { date: 'Thu', score: 0.80, positive: 28, neutral: 5, negative: 2, volume: 35 },
      { date: 'Fri', score: 0.82, positive: 32, neutral: 4, negative: 1, volume: 37 },
    ],
  },
}

export const aggregatePolarity: PolarityData[] = [
  { name: 'Positive', value: 68, color: '#10b981' }, // emerald-500
  { name: 'Neutral', value: 21, color: '#64748b' },  // slate-500
  { name: 'Negative', value: 11, color: '#f43f5e' }, // rose-500
]

