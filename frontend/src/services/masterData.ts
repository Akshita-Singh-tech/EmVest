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
  { symbol: 'RELIANCE', name: 'Reliance Industries Ltd', sector: 'Energy, Oil & Gas', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1328.4 },
  { symbol: 'TCS', name: 'Tata Consultancy Services Ltd', sector: 'Information Technology', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 4120.0 },
  { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1745.8 },
  { symbol: 'INFY', name: 'Infosys Ltd', sector: 'Information Technology', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1890.15 },
  { symbol: 'ICICIBANK', name: 'ICICI Bank Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1265.5 },
  { symbol: 'BHARTIARTL', name: 'Bharti Airtel Ltd', sector: 'Telecommunications', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1610.2 },
  { symbol: 'SBIN', name: 'State Bank of India', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 832.4 },
  { symbol: 'LICI', name: 'Life Insurance Corporation of India', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 945.0 },
  { symbol: 'ITC', name: 'ITC Ltd', sector: 'Fast Moving Consumer Goods (FMCG)', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 492.3 },
  { symbol: 'HINDUNILVR', name: 'Hindustan Unilever Ltd', sector: 'Fast Moving Consumer Goods (FMCG)', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 2450.0 },
  { symbol: 'LT', name: 'Larsen & Toubro Ltd', sector: 'Infrastructure & Capital Goods', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 3620.5 },
  { symbol: 'TATAMOTORS', name: 'Tata Motors Ltd', sector: 'Automobile & Auto Ancillary', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 840.1 },
  { symbol: 'BAJFINANCE', name: 'Bajaj Finance Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 6850.0 },
  { symbol: 'MARUTI', name: 'Maruti Suzuki India Ltd', sector: 'Automobile & Auto Ancillary', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 11450.0 },
  { symbol: 'SUNPHARMA', name: 'Sun Pharmaceutical Industries Ltd', sector: 'Pharmaceuticals & Healthcare', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1840.0 },
  { symbol: 'KOTAKBANK', name: 'Kotak Mahindra Bank Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1780.0 },
  { symbol: 'TITAN', name: 'Titan Company Ltd', sector: 'Consumer Discretionary', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 3280.0 },
  { symbol: 'AXISBANK', name: 'Axis Bank Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1195.0 },
  { symbol: 'WIPRO', name: 'Wipro Ltd', sector: 'Information Technology', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 560.2 },
  { symbol: 'ONGC', name: 'Oil & Natural Gas Corporation Ltd', sector: 'Energy, Oil & Gas', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 260.4 },
  { symbol: 'NTPC', name: 'NTPC Ltd', sector: 'Energy, Oil & Gas', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 380.5 },
  { symbol: 'ASIANPAINT', name: 'Asian Paints Ltd', sector: 'Consumer Discretionary', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 2540.0 },
  { symbol: 'ULTRACEMCO', name: 'UltraTech Cement Ltd', sector: 'Infrastructure & Capital Goods', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 11200.0 },
  { symbol: 'POWERGRID', name: 'Power Grid Corporation of India', sector: 'Energy, Oil & Gas', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 320.0 },
  { symbol: 'COALINDIA', name: 'Coal India Ltd', sector: 'Metals & Mining', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 425.0 },
  { symbol: 'TATASTEEL', name: 'Tata Steel Ltd', sector: 'Metals & Mining', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 148.5 },
  { symbol: 'BAJAJFINSV', name: 'Bajaj Finserv Ltd', sector: 'Banking & Financial Services', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1620.0 },
  { symbol: 'HCLTECH', name: 'HCL Technologies Ltd', sector: 'Information Technology', exchange: 'NSE/BSE', marketCapCategory: 'Large Cap', basePrice: 1850.0 },
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

