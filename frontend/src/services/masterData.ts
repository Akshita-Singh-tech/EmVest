import type { MasterCompany } from '../types/personalization'

export const masterSectors = [
  'Banking & Financial Services',
  'Information Technology',
  'Automobile & Auto Ancillary',
  'Energy, Oil & Gas',
  'Pharmaceuticals & Healthcare',
  'Fast Moving Consumer Goods (FMCG)',
  'Metals & Mining',
  'Infrastructure & Capital Goods',
  'Telecommunications',
  'Consumer Discretionary',
]

export const masterCompanyList: MasterCompany[] = [
  { symbol: 'RELIANCE', name: 'Reliance Industries Ltd', sector: 'Energy, Oil & Gas', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1320.0 },
  { symbol: 'TCS', name: 'Tata Consultancy Services Ltd', sector: 'Information Technology', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 2498.5 },
  { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 788.25 },
  { symbol: 'INFY', name: 'Infosys Ltd', sector: 'Information Technology', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1181.4 },
  { symbol: 'ICICIBANK', name: 'ICICI Bank Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1571.2 },
  { symbol: 'BHARTIARTL', name: 'Bharti Airtel Ltd', sector: 'Telecommunications', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 2107.2 },
  { symbol: 'SBIN', name: 'State Bank of India', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1018.5 },
  { symbol: 'LICI', name: 'Life Insurance Corporation of India', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 394.0 },
  { symbol: 'ITC', name: 'ITC Ltd', sector: 'Fast Moving Consumer Goods (FMCG)', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 283.15 },
  { symbol: 'HINDUNILVR', name: 'Hindustan Unilever Ltd', sector: 'Fast Moving Consumer Goods (FMCG)', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1998.4 },
  { symbol: 'LT', name: 'Larsen & Toubro Ltd', sector: 'Infrastructure & Capital Goods', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 4117.7 },
  { symbol: 'TATAMOTORS', name: 'Tata Motors Ltd', sector: 'Automobile & Auto Ancillary', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 292.0 },
  { symbol: 'BAJFINANCE', name: 'Bajaj Finance Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1087.75 },
  { symbol: 'MARUTI', name: 'Maruti Suzuki India Ltd', sector: 'Automobile & Auto Ancillary', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 12750.0 },
  { symbol: 'SUNPHARMA', name: 'Sun Pharmaceutical Industries Ltd', sector: 'Pharmaceuticals & Healthcare', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1840.0 },
  { symbol: 'KOTAKBANK', name: 'Kotak Mahindra Bank Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 480.0 },
  { symbol: 'TITAN', name: 'Titan Company Ltd', sector: 'Consumer Discretionary', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 5000.0 },
  { symbol: 'AXISBANK', name: 'Axis Bank Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1322.9 },
  { symbol: 'WIPRO', name: 'Wipro Ltd', sector: 'Information Technology', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 198.0 },
  { symbol: 'ONGC', name: 'Oil & Natural Gas Corporation Ltd', sector: 'Energy, Oil & Gas', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 231.76 },
  { symbol: 'NTPC', name: 'NTPC Ltd', sector: 'Energy, Oil & Gas', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 323.45 },
  { symbol: 'ASIANPAINT', name: 'Asian Paints Ltd', sector: 'Consumer Discretionary', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 2546.0 },
  { symbol: 'ULTRACEMCO', name: 'UltraTech Cement Ltd', sector: 'Infrastructure & Capital Goods', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 12450.0 },
  { symbol: 'POWERGRID', name: 'Power Grid Corporation of India', sector: 'Energy, Oil & Gas', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 259.9 },
  { symbol: 'COALINDIA', name: 'Coal India Ltd', sector: 'Metals & Mining', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 400.0 },
  { symbol: 'TATASTEEL', name: 'Tata Steel Ltd', sector: 'Metals & Mining', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 186.3 },
  { symbol: 'BAJAJFINSV', name: 'Bajaj Finserv Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1864.7 },
  { symbol: 'HCLTECH', name: 'HCL Technologies Ltd', sector: 'Information Technology', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1440.0 },
  { symbol: 'ZOMATO', name: 'Zomato Ltd', sector: 'Consumer Discretionary', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 265.0 },
  { symbol: 'JIOFIN', name: 'Jio Financial Services Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 315.0 },
]

export function searchMasterCompanies(query: string, sectorFilter?: string): MasterCompany[] {
  let results = [...masterCompanyList]

  if (sectorFilter && sectorFilter !== 'All Sectors') {
    results = results.filter((c) => c.sector === sectorFilter)
  }

  if (query && query.trim()) {
    const q = query.toLowerCase().trim()
    results = results.filter(
      (c) =>
        c.symbol.toLowerCase().includes(q) ||
        c.name.toLowerCase().includes(q) ||
        c.sector.toLowerCase().includes(q)
    )
  }

  return results
}

export function getCompanyBySymbol(symbol: string): MasterCompany | undefined {
  return masterCompanyList.find((c) => c.symbol.toUpperCase() === symbol.toUpperCase())
}

