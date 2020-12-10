# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0

from ..math_and_stats import sigmoid

# this one can be modified
ticker_group_dict = {'All': [],
                     'Basic Materials': ['DOW','HUN','EXP','AVTR','ECL','APD','DD','FNV','NEM','GDX','XLB'],
                     'Communication Services': ['CMCSA','DIS','EA','FB','GOOG','GOOGL','NFLX','ROKU','TMUS','VZ','ZM','T','TWTR','IRDM','TWLO','ESPO','XLC'],
                     'Consumer Cyclical': ['AMZN','BABA','HD','LOW','F','FIVE','JD','M','MCD','LGIH','MELI','PTON','NIO','NKE','OSTK','TSLA','TM','ARD','BERY','SBUX','BKNG','NCLH','W','XLY','FCAU'],
                     'Consumer Defensive': ['BYND','KO','PG','COST','TGT','WMT','GIS','ACI','OLLI','SAM','PEP','XLP'],
                     'Energy': ['CVX','MUR','VLO','EQT','XOM','TOT','XLE'],
                     'Financial Services': ['AXP','BAC', 'BRK-B','C','GS','JPM','TRV','V','MA','WFC','MS','XLF','PYPL','BHF','MSCI','JEF'],
                     'Healthcare': ['ABT','ALGN','AMGN','BMY','INO','JNJ','MRK','MRNA','PFE','UNH','NVS','WBA','ABBV','BIIB','QDEL','LVGO','TLRY','ISRG','GILD','TMO','XLV'],
                     'Industrials': ['BA', 'CAT', 'DAL', 'FDX', 'HON', 'MMM','SPCE','LMT','UAL','EAF','ENR','GNRC','KODK','RTX','GE','WM','AAL','XLI'],
                     'Technology': ['AAPL','ADBE','AMD','AYX','CLDR','CRM','CRWD','CSCO','ENPH','FEYE','IBM','INTC','MSFT','NVDA','NVMI','NLOK','ONTO','QCOM','SPLK','TSM','UBER','FIT','SQ','CTXS','DOCU','LRCX','MCHP','MU','NXPI','SHOP','STMP','TXN','NOW','SNE','WDAY','XLK'],
                     'Utilities': ['PCG','D','DUK','XEL','NRG','ES','XLU'],
                     'Real Estate': ['AMT','CCI','PLD','BPYU','BDN','CSGP','XLRE'],
                     'Dividend Stocks (11/2020)': ['BMY','WMT','HD','AAPL','MSFT'],
                     'Growth Stocks (11/2020)': ['ALGN','FIVE','LGIH','MELI','PTON'],
                     'ETF / ETN': ['JETS', 'ONEQ', 'IEMG', 'VTHR', 'IWB', 'IWM', 'IWV', 'IWF', 'VTV', 'SCHD', 'USMV', 'VEA', 'VWO', 'AGG', 'LQD', 'GLD', 'VTI', 'DIA', 'OILU', 'OILD', 'TQQQ', 'SQQQ', 'UDOW', 'SDOW', 'UVXY', 'SVXY', 'KORU', 'YANG', 'YINN', 'QQQ', 'VOO','SPY','IVV','TMF','TMV','TBF','TLT','ESPO','GDX','XLC','XLI','XLF','XLE','XLV','XLB','XLK','XLU','XLP','XLY','XLRE'],
                     'Major Market Indices': ['DIA','SPLG','IVV','VOO','SPY','QQQ','ONEQ','IWM','VTWO','VXX'],
                     'DOW 30': ['GS','WMT','MCD','CRM','DIS','NKE','CAT','TRV','VZ','JPM','IBM','HD','INTC','AAPL','MMM','MSFT','JNJ','CSCO','V','DOW','MRK','PG','AXP','KO','AMGN','HON','UNH','WBA','CVX','BA'],
                     'NASDAQ 100': ['AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMD', 'AMGN', 'AMZN', 'ANSS', 'ASML', 'ATVI', 'AVGO', 'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CDNS', 'CDW', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CPRT', 'CSCO', 'CSX', 'CTAS', 'CTSH', 'CTXS', 'DLTR', 'DOCU', 'DXCM', 'EA', 'EBAY', 'EXC', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX', 'FOXA', 'GILD', 'GOOG', 'GOOGL', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JD', 'KDP', 'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'LULU', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MRNA', 'MSFT', 'MU', 'MXIM', 'NFLX', 'NTES', 'NVDA', 'NXPI', 'ORLY', 'PAYX', 'PCAR', 'PDD', 'PEP', 'PYPL', 'QCOM', 'REGN', 'ROST', 'SBUX', 'SGEN', 'SIRI', 'SNPS', 'SPLK', 'SWKS', 'TCOM', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'ULTA', 'VRSK', 'VRSN', 'VRTX', 'WBA', 'WDAY', 'XEL', 'XLNX', 'ZM'],
                     'S&P 500': ['VOO','SPY','IVV','MMM','ABT','ABBV','ABMD','ACN','ATVI','ADBE','AMD','AAP','AES','AFL','A','APD','AKAM','ALK','ALB','ARE','ALXN','ALGN','ALLE','LNT','ALL','GOOGL','GOOG','MO','AMZN','AMCR','AEE','AAL','AEP','AXP','AIG','AMT','AWK','AMP','ABC','AME','AMGN','APH','ADI','ANSS','ANTM','AON','AOS','APA','AIV','AAPL','AMAT','APTV','ADM','ANET','AJG','AIZ','T','ATO','ADSK','ADP','AZO','AVB','AVY','BKR','BLL','BAC','BK','BAX','BDX','BRK-B','BBY','BIO','BIIB','BLK','BA','BKNG','BWA','BXP','BSX','BMY','AVGO','BR','BF-B','CHRW','COG','CDNS','CPB','COF','CAH','KMX','CCL','CARR','CTLT','CAT','CBOE','CBRE','CDW','CE','CNC','CNP','CERN','CF','SCHW','CHTR','CVX','CMG','CB','CHD','CI','CINF','CTAS','CSCO','C','CFG','CTXS','CLX','CME','CMS','KO','CTSH','CL','CMCSA','CMA','CAG','CXO','COP','ED','STZ','COO','CPRT','GLW','CTVA','COST','CCI','CSX','CMI','CVS','DHI','DHR','DRI','DVA','DE','DAL','XRAY','DVN','DXCM','FANG','DLR','DFS','DISCA','DISCK','DISH','DG','DLTR','D','DPZ','DOV','DOW','DTE','DUK','DRE','DD','DXC','EMN','ETN','EBAY','ECL','EIX','EW','EA','EMR','ETR','EOG','EFX','EQIX','EQR','ESS','EL','ETSY','EVRG','ES','RE','EXC','EXPE','EXPD','EXR','XOM','FFIV','FB','FAST','FRT','FDX','FIS','FITB','FE','FRC','FISV','FLT','FLIR','FLS','FMC','F','FTNT','FTV','FBHS','FOXA','FOX','BEN','FCX','GPS','GRMN','IT','GD','GE','GIS','GM','GPC','GILD','GL','GPN','GS','GWW','HAL','HBI','HIG','HAS','HCA','PEAK','HSIC','HSY','HES','HPE','HLT','HFC','HOLX','HD','HON','HRL','HST','HWM','HPQ','HUM','HBAN','HII','IEX','IDXX','INFO','ITW','ILMN','INCY','IR','INTC','ICE','IBM','IP','IPG','IFF','INTU','ISRG','IVZ','IPGP','IQV','IRM','JKHY','J','JBHT','SJM','JNJ','JCI','JPM','JNPR','KSU','K','KEY','KEYS','KMB','KIM','KMI','KLAC','KHC','KR','LB','LHX','LH','LRCX','LW','LVS','LEG','LDOS','LEN','LLY','LNC','LIN','LYV','LKQ','LMT','L','LOW','LUMN','LYB','MTB','MRO','MPC','MKTX','MAR','MMC','MLM','MAS','MA','MKC','MXIM','MCD','MCK','MDT','MRK','MET','MTD','MGM','MCHP','MU','MSFT','MAA','MHK','TAP','MDLZ','MNST','MCO','MS','MOS','MSI','MSCI','NDAQ','NOV','NTAP','NFLX','NWL','NEM','NWSA','NWS','NEE','NLSN','NKE','NI','NSC','NTRS','NOC','NLOK','NCLH','NRG','NUE','NVDA','NVR','ORLY','OXY','ODFL','OMC','OKE','ORCL','OTIS','PCAR','PKG','PH','PAYX','PAYC','PYPL','PNR','PBCT','PEP','PKI','PRGO','PFE','PM','PSX','PNW','PXD','PNC','POOL','PPG','PPL','PFG','PG','PGR','PLD','PRU','PEG','PSA','PHM','PVH','QRVO','PWR','QCOM','DGX','RL','RJF','RTX','O','REG','REGN','RF','RSG','RMD','RHI','ROK','ROL','ROP','ROST','RCL','SPGI','CRM','SBAC','SLB','STX','SEE','SRE','NOW','SHW','SPG','SWKS','SLG','SNA','SO','LUV','SWK','SBUX','STT','STE','SYK','SIVB','SYF','SNPS','SYY','TMUS','TROW','TTWO','TPR','TGT','TEL','FTI','TDY','TFX','TER','TSLA','TXT','TMO','TIF','TJX','TSCO','TT','TDG','TRV','TFC','TWTR','TYL','TSN','UDR','ULTA','USB','UAA','UA','UNP','UAL','UNH','UPS','URI','UHS','UNM','VLO','VAR','VTR','VTRS','VRSN','VRSK','VZ','VRTX','VFC','VIAC','V','VNT','VNO','VMC','WRB','WAB','WMT','WBA','DIS','WM','WAT','WEC','WFC','WELL','WST','WDC','WU','WRK','WY','WHR','WMB','WLTW','WYNN','XEL','XRX','XLNX','XYL','YUM','ZBRA','ZBH','ZION','ZTS'],
                     'Russell 1000': ['A', 'AAL', 'AAP', 'AAPL', 'AAXN', 'ABBV', 'ABC', 'ABMD', 'ABT', 'ACAD', 'ACC', 'ACGL', 'ACHC', 'ACI', 'ACM', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADPT', 'ADS', 'ADSK', 'ADT', 'AEE', 'AEP', 'AES', 'AFG', 'AFL', 'AGCO', 'AGIO', 'AGNC', 'AGO', 'AGR', 'AIG', 'AIV', 'AIZ', 'AJG', 'AKAM', 'AL', 'ALB', 'ALGN', 'ALK', 'ALKS', 'ALL', 'ALLE', 'ALLY', 'ALNY', 'ALSN', 'ALXN', 'AM', 'AMAT', 'AMCR', 'AMD', 'AME', 'AMED', 'AMG', 'AMGN', 'AMH', 'AMP', 'AMT', 'AMZN', 'AN', 'ANAT', 'ANET', 'ANSS', 'ANTM', 'AON', 'AOS', 'APA', 'APD', 'APH', 'APLE', 'APO', 'APTV', 'ARD', 'ARE', 'ARES', 'ARMK', 'ARW', 'ASB', 'ASH', 'ATH', 'ATO', 'ATR', 'ATUS', 'ATVI', 'AVB', 'AVGO', 'AVLR', 'AVT', 'AVTR', 'AVY', 'AWI', 'AWK', 'AXP', 'AXS', 'AXTA', 'AYI', 'AYX', 'AZEK', 'AZO', 'AZPN', 'BA', 'BAC', 'BAH', 'BAX', 'BBY', 'BC', 'BDN', 'BDX', 'BEN', 'BERY', 'BF-A', 'BFAM', 'BF-B', 'BG', 'BHF', 'BIGC', 'BIIB', 'BILL', 'BIO', 'BK', 'BKI', 'BKNG', 'BKR', 'BLI', 'BLK', 'BLL', 'BLUE', 'BMRN', 'BMY', 'BOH', 'BOKF', 'BPOP', 'BPYU', 'BR', 'BRK-B', 'BRKR', 'BRO', 'BRX', 'BSX', 'BURL', 'BWA', 'BWXT', 'BXP', 'BYND', 'C', 'CABO', 'CACC', 'CACI', 'CAG', 'CAH', 'CARR', 'CASY', 'CAT', 'CB', 'CBOE', 'CBRE', 'CBSH', 'CBT', 'CC', 'CCI', 'CCK', 'CCL', 'CDAY', 'CDK', 'CDNS', 'CDW', 'CE', 'CERN', 'CF', 'CFG', 'CFR', 'CFX', 'CG', 'CGNX', 'CHD', 'CHE', 'CHGG', 'CHH', 'CHNG', 'CHRW', 'CHTR', 'CI', 'CIEN', 'CINF', 'CL', 'CLGX', 'CLH', 'CLR', 'CLX', 'CMA', 'CMCSA', 'CME', 'CMG', 'CMI', 'CMS', 'CNA', 'CNC', 'CNP', 'COF', 'COG', 'COHR', 'COLD', 'COLM', 'COMM', 'CONE', 'COO', 'COP', 'COR', 'COST', 'COTY', 'COUP', 'CPA', 'CPB', 'CPRI', 'CPRT', 'CPT', 'CR', 'CREE', 'CRI', 'CRL', 'CRM', 'CRUS', 'CRWD', 'CSCO', 'CSGP', 'CSL', 'CSX', 'CTAS', 'CTLT', 'CTSH', 'CTVA', 'CTXS', 'CUBE', 'CUZ', 'CVNA', 'CVS', 'CVX', 'CW', 'CXO', 'D', 'DAL', 'DBX', 'DCI', 'DCT', 'DD', 'DDOG', 'DE', 'DEI', 'DELL', 'DFS', 'DG', 'DGX', 'DHI', 'DHR', 'DIS', 'DISCA', 'DISCK', 'DISH', 'DKS', 'DLB', 'DLR', 'DLTR', 'DNB', 'DNKN', 'DOCU', 'DOV', 'DOW', 'DOX', 'DPZ', 'DRE', 'DRI', 'DT', 'DTE', 'DUK', 'DVA', 'DVN', 'DXC', 'DXCM', 'EA', 'EAF', 'EBAY', 'ECL', 'ED', 'EEFT', 'EFX', 'EHC', 'EIX', 'EL', 'ELAN', 'ELS', 'EMN', 'EMR', 'ENPH', 'ENR', 'ENTG', 'EOG', 'EPAM', 'EPR', 'EQC', 'EQH', 'EQIX', 'EQR', 'EQT', 'ERIE', 'ES', 'ESI', 'ESRT', 'ESS', 'ESTC', 'ETN', 'ETR', 'ETRN', 'ETSY', 'EV', 'EVBG', 'EVR', 'EVRG', 'EW', 'EWBC', 'EXAS', 'EXC', 'EXEL', 'EXP', 'EXPD', 'EXPE', 'EXR', 'F', 'FAF', 'FANG', 'FAST', 'FB', 'FBHS', 'FCN', 'FCNCA', 'FCX', 'FDS', 'FDX', 'FE', 'FEYE', 'FFIV', 'FHB', 'FHN', 'FICO', 'FIS', 'FISV', 'FITB', 'FIVE', 'FIVN', 'FL', 'FLIR', 'FLO', 'FLS', 'FLT', 'FMC', 'FNB', 'FND', 'FNF', 'FOX', 'FOXA', 'FR', 'FRC', 'FRT', 'FSLR', 'FSLY', 'FTDR', 'FTNT', 'FTV', 'FWONA', 'FWONK', 'G', 'GBT', 'GD', 'GDDY', 'GE', 'GGG', 'GH', 'GHC', 'GILD', 'GIS', 'GL', 'GLIBA', 'GLOB', 'GLPI', 'GLW', 'GM', 'GMED', 'GNRC', 'GNTX', 'GO', 'GOCO', 'GOOG', 'GOOGL', 'GPC', 'GPK', 'GPN', 'GPS', 'GRA', 'GRMN', 'GRUB', 'GS', 'GTES', 'GWRE', 'GWW', 'H', 'HAE', 'HAIN', 'HAL', 'HAS', 'HBAN', 'HBI', 'HCA', 'HD', 'HDS', 'HE', 'HEI', 'HEI-A', 'HES', 'HFC', 'HHC', 'HIG', 'HII', 'HIW', 'HLF', 'HLT', 'HOG', 'HOLX', 'HON', 'HP', 'HPE', 'HPP', 'HPQ', 'HRB', 'HRC', 'HRL', 'HSIC', 'HST', 'HSY', 'HTA', 'HUBB', 'HUBS', 'HUM', 'HUN', 'HWM', 'HXL', 'HZNP', 'IAA', 'IAC', 'IART', 'IBKR', 'IBM', 'ICE', 'ICUI', 'IDA', 'IDXX', 'IEX', 'IFF', 'ILMN', 'INCY', 'INFO', 'INGR', 'INTC', 'INTU', 'INVH', 'IONS', 'IOVA', 'IP', 'IPG', 'IPGP', 'IPHI', 'IQV', 'IR', 'IRM', 'ISRG', 'IT', 'ITT', 'ITW', 'IVZ', 'J', 'JAMF', 'JAZZ', 'JBGS', 'JBHT', 'JBL', 'JBLU', 'JCI', 'JEF', 'JKHY', 'JLL', 'JNJ', 'JNPR', 'JPM', 'JW-A', 'JWN', 'K', 'KDP', 'KEX', 'KEY', 'KEYS', 'KHC', 'KIM', 'KKR', 'KLAC', 'KMB', 'KMI', 'KMPR', 'KMX', 'KNX', 'KO', 'KR', 'KRC', 'KSS', 'KSU', 'L', 'LAMR', 'LAZ', 'LB', 'LBRDA', 'LBRDK', 'LDOS', 'LEA', 'LECO', 'LEG', 'LEN', 'LEN-B', 'LFUS', 'LGF-A', 'LGF-B', 'LH', 'LHX', 'LII', 'LIN', 'LITE', 'LKQ', 'LLY', 'LMND', 'LMT', 'LNC', 'LNG', 'LNT', 'LOPE', 'LOW', 'LPLA', 'LRCX', 'LSI', 'LSTR', 'LSXMA', 'LSXMK', 'LULU', 'LUMN', 'LUV', 'LVS', 'LW', 'LYB', 'LYFT', 'LYV', 'MA', 'MAA', 'MAN', 'MANH', 'MAR', 'MAS', 'MASI', 'MAT', 'MCD', 'MCHP', 'MCK', 'MCO', 'MCY', 'MDB', 'MDLA', 'MDLZ', 'MDT', 'MDU', 'MET', 'MGM', 'MHK', 'MIC', 'MIDD', 'MKC', 'MKL', 'MKSI', 'MKTX', 'MLM', 'MMC', 'MMM', 'MNST', 'MO', 'MOH', 'MORN', 'MOS', 'MPC', 'MPW', 'MPWR', 'MRCY', 'MRK', 'MRNA', 'MRO', 'MRVL', 'MS', 'MSA', 'MSCI', 'MSFT', 'MSGE', 'MSGS', 'MSI', 'MSM', 'MTB', 'MTCH', 'MTD', 'MTG', 'MTN', 'MU', 'MUR', 'MXIM', 'NATI', 'NBIX', 'NCLH', 'NCNO', 'NCR', 'NDAQ', 'NDSN', 'NEE', 'NEM', 'NET', 'NEU', 'NEWR', 'NFG', 'NFLX', 'NI', 'NKE', 'NKTR', 'NLOK', 'NLSN', 'NLY', 'NNN', 'NOC', 'NOV', 'NOW', 'NRG', 'NRZ', 'NSC', 'NTAP', 'NTNX', 'NTRS', 'NUAN', 'NUE', 'NUS', 'NVCR', 'NVDA', 'NVR', 'NVST', 'NVT', 'NWL', 'NWS', 'NWSA', 'NXST', 'NYCB', 'NYT', 'O', 'OC', 'ODFL', 'OFC', 'OGE', 'OHI', 'OKE', 'OKTA', 'OLED', 'OLLI', 'OLN', 'OMC', 'OMF', 'ON', 'ORCL', 'ORI', 'ORLY', 'OSH', 'OSK', 'OTIS', 'OUT', 'OXY', 'OZK', 'PACW', 'PAG', 'PANW', 'PAYC', 'PAYX', 'PB', 'PBCT', 'PCAR', 'PCG', 'PCTY', 'PD', 'PE', 'PEAK', 'PEG', 'PEGA', 'PEN', 'PEP', 'PFE', 'PFG', 'PFPT', 'PG', 'PGR', 'PGRE', 'PH', 'PHM', 'PII', 'PINC', 'PINS', 'PK', 'PKG', 'PKI', 'PLAN', 'PLD', 'PLNT', 'PM', 'PNC', 'PNFP', 'PNR', 'PNW', 'PODD', 'POOL', 'POST', 'PPC', 'PPD', 'PPG', 'PPL', 'PRAH', 'PRGO', 'PRI', 'PRU', 'PS', 'PSA', 'PSTG', 'PSX', 'PTC', 'PTON', 'PVH', 'PWR', 'PXD', 'PYPL', 'QCOM', 'QDEL', 'QGEN', 'QRTEA', 'QRVO', 'R', 'RBC', 'RCL', 'RE', 'REG', 'REGN', 'RETA', 'REXR', 'REYN', 'RF', 'RGA', 'RGEN', 'RGLD', 'RHI', 'RJF', 'RKT', 'RL', 'RMD', 'RNG', 'RNR', 'ROK', 'ROKU', 'ROL', 'ROP', 'ROST', 'RP', 'RPM', 'RPRX', 'RS', 'RSG', 'RTX', 'RYN', 'SABR', 'SAGE', 'SAIC', 'SAM', 'SATS', 'SBAC', 'SBNY', 'SBUX', 'SC', 'SCCO', 'SCHW', 'SCI', 'SEB', 'SEDG', 'SEE', 'SEIC', 'SFM', 'SGEN', 'SHW', 'SIRI', 'SIVB', 'SIX', 'SJM', 'SKX', 'SLB', 'SLG', 'SLGN', 'SLM', 'SMAR', 'SMG', 'SNA', 'SNDR', 'SNPS', 'SNV', 'SNX', 'SO', 'SON', 'SPB', 'SPCE', 'SPG', 'SPGI', 'SPLK', 'SPOT', 'SPR', 'SQ', 'SRC', 'SRCL', 'SRE', 'SRPT', 'SSNC', 'ST', 'STAY', 'STE', 'STL', 'STLD', 'STNE', 'STOR', 'STT', 'STWD', 'STZ', 'SUI', 'SWCH', 'SWI', 'SWK', 'SWKS', 'SYF', 'SYK', 'SYNH', 'SYY', 'T', 'TAP', 'TCF', 'TCO', 'TDC', 'TDG', 'TDOC', 'TDS', 'TDY', 'TEAM', 'TECH', 'TER', 'TFC', 'TFSL', 'TFX', 'TGT', 'THG', 'THO', 'THS', 'TIF', 'TJX', 'TKR', 'TMO', 'TMUS', 'TMX', 'TNDM', 'TOL', 'TPR', 'TPX', 'TREE', 'TREX', 'TRGP', 'TRIP', 'TRMB', 'TRN', 'TROW', 'TRU', 'TRV', 'TSCO', 'TSLA', 'TSN', 'TT', 'TTC', 'TTD', 'TTWO', 'TW', 'TWLO', 'TWOU', 'TWTR', 'TXG', 'TXN', 'TXT', 'TYL', 'UA', 'UAA', 'UAL', 'UBER', 'UDR', 'UGI', 'UHAL', 'UHS', 'UI', 'ULTA', 'UMPQ', 'UNH', 'UNM', 'UNP', 'UNVR', 'UPS', 'URI', 'USB', 'USFD', 'USM', 'UTHR', 'V', 'VAR', 'VEEV', 'VER', 'VFC', 'VIAC', 'VIACA', 'VICI', 'VIRT', 'VLO', 'VMC', 'VMI', 'VMW', 'VNO', 'VNT', 'VOYA', 'VRM', 'VRSK', 'VRSN', 'VRT', 'VRTX', 'VSAT', 'VST', 'VTR', 'VTRS', 'VVV', 'VZ', 'W', 'WAB', 'WAL', 'WAT', 'WBA', 'WBS', 'WDAY', 'WDC', 'WEC', 'WELL', 'WEN', 'WEX', 'WFC', 'WH', 'WHR', 'WLK', 'WLTW', 'WM', 'WMB', 'WMT', 'WORK', 'WPC', 'WPX', 'WRB', 'WRI', 'WRK', 'WSM', 'WSO', 'WST', 'WTFC', 'WTM', 'WTRG', 'WU', 'WWD', 'WWE', 'WY', 'WYND', 'WYNN', 'XEC', 'XEL', 'XLNX', 'XLRN', 'XOM', 'XPO', 'XRAY', 'XRX', 'XYL', 'Y', 'YUM', 'YUMC', 'Z', 'ZBH', 'ZBRA', 'ZEN', 'ZG', 'ZION', 'ZM', 'ZNGA', 'ZS', 'ZTS'],
                     'NASDAQ Composite': ['AAL', 'AAON', 'AAPL', 'AAWW', 'AAXN', 'ABCB', 'ABMD', 'ACAD', 'ACCD', 'ACET', 'ACGL', 'ACHC', 'ACIA', 'ACIW', 'ACMR', 'ACRS', 'ACRX', 'ADBE', 'ADI', 'ADP', 'ADPT', 'ADSK', 'ADUS', 'ADVM', 'AEGN', 'AEIS', 'AEP', 'AFIN', 'AFYA', 'AGFS', 'AGIO', 'AGNC', 'AHCO', 'AIMC', 'AKAM', 'AKRO', 'ALEC', 'ALGM', 'ALGN', 'ALGT', 'ALKS', 'ALLK', 'ALLO', 'ALNY', 'ALRM', 'ALRN', 'ALTA', 'ALTM', 'ALTR', 'ALVR', 'ALXN', 'ALXO', 'AMAT', 'AMBA', 'AMD', 'AMED', 'AMGN', 'AMKR', 'AMPH', 'AMRN', 'AMSF', 'AMTI', 'AMWD', 'AMZN', 'ANAT', 'ANSS', 'APA', 'APHA', 'APLS', 'APPF', 'APPN', 'APPS', 'ARCB', 'ARCE', 'ARCT', 'ARGX', 'ARLP', 'ARNA', 'ARRY', 'ARVN', 'ARWR', 'ASML', 'ASND', 'ASRT', 'ASTE', 'ATNI', 'ATNX', 'ATRA', 'ATRC', 'ATRI', 'ATSG', 'ATVI', 'AUB', 'AUPH', 'AVAV', 'AVGO', 'AVIR', 'AVRO', 'AVT', 'AXNX', 'AXSM', 'AY', 'AZN', 'AZPN', 'BAND', 'BANF', 'BANR', 'BATRK', 'BBBY', 'BBIO', 'BCPC', 'BDGE', 'BDTX', 'BEAM', 'BEAT', 'BECN', 'BGNE', 'BHF', 'BIDU', 'BIGC', 'BIIB', 'BILI', 'BKEP', 'BKNG', 'BL', 'BLCM', 'BLDP', 'BLDR', 'BLI', 'BLKB', 'BLMN', 'BLUE', 'BMCH', 'BMRN', 'BNTX', 'BOKF', 'BPFH', 'BPMC', 'BPOP', 'BPY', 'BRID', 'BRKL', 'BRKR', 'BRKS', 'BSY', 'BTAI', 'BUSE', 'BYND', 'BZUN', 'CAC', 'CACC', 'CAKE', 'CALM', 'CAR', 'CARG', 'CASH', 'CASS', 'CASY', 'CATY', 'CBPO', 'CBRL', 'CBSH', 'CCLP', 'CCMP', 'CCOI', 'CCXI', 'CDK', 'CDLX', 'CDNA', 'CDNS', 'CDW', 'CELH', 'CENTA', 'CERN', 'CERS', 'CFFN', 'CG', 'CGNX', 'CHCO', 'CHDN', 'CHKP', 'CHNG', 'CHRS', 'CHRW', 'CHTR', 'CIGI', 'CINF', 'CMCO', 'CMCSA', 'CME', 'CMPR', 'CNOB', 'CNSL', 'CNST', 'CNXN', 'COHR', 'COKE', 'COLB', 'COLM', 'COMM', 'CONE', 'COOP', 'CORE', 'CORT', 'COST', 'COUP', 'CPRT', 'CREE', 'CRNC', 'CRON', 'CROX', 'CRSP', 'CRSR', 'CRTO', 'CRTX', 'CRUS', 'CRVL', 'CRWD', 'CSCO', 'CSGP', 'CSGS', 'CSII', 'CSIQ', 'CSOD', 'CSTE', 'CSX', 'CTAS', 'CTBI', 'CTRE', 'CTSH', 'CTXS', 'CVAC', 'CVBF', 'CVCO', 'CVET', 'CVGW', 'CVLT', 'CWST', 'CYBR', 'CYCN', 'CYRX', 'CYTK', 'CZR', 'DBX', 'DCPH', 'DCT', 'DDOG', 'DHC', 'DHIL', 'DIOD', 'DISCA', 'DISCK', 'DISH', 'DKNG', 'DLTR', 'DNKN', 'DNLI', 'DOCU', 'DOMO', 'DOOO', 'DORM', 'DOX', 'DRNA', 'DSGX', 'DXCM', 'EA', 'EBAY', 'EBC', 'EBSB', 'EBTC', 'ECOL', 'ECOR', 'ECPG', 'EDIT', 'EEFT', 'EFSC', 'EGBN', 'EGOV', 'EHTH', 'EIDX', 'ELOX', 'ENPH', 'ENSG', 'ENTA', 'ENTG', 'EPAY', 'EPZM', 'EQIX', 'ERIC', 'ERIE', 'ESGR', 'ESLT', 'ESPR', 'ETSY', 'EVBG', 'EVOP', 'EWBC', 'EXAS', 'EXC', 'EXEL', 'EXLS', 'EXPD', 'EXPE', 'EXPI', 'EXPO', 'EYE', 'EYEG', 'FANG', 'FANH', 'FARO', 'FAST', 'FATE', 'FB', 'FBNC', 'FBRX', 'FCFS', 'FCNCA', 'FELE', 'FEYE', 'FFBC', 'FFIC', 'FFIN', 'FFIV', 'FGEN', 'FHB', 'FIBK', 'FISV', 'FITB', 'FIVE', 'FIVN', 'FIZZ', 'FLEX', 'FLIC', 'FLIR', 'FLWS', 'FMAO', 'FMBI', 'FMTX', 'FNLC', 'FOCS', 'FOLD', 'FORM', 'FORR', 'FOX', 'FOXA', 'FOXF', 'FPRX', 'FRG', 'FRHC', 'FRME', 'FROG', 'FRPT', 'FRTA', 'FSLR', 'FSV', 'FTDR', 'FTNT', 'FULT', 'FUTU', 'FWONK', 'FWRD', 'GABC', 'GASS', 'GBCI', 'GBT', 'GDEN', 'GDS', 'GEOS', 'GH', 'GILD', 'GLIBA', 'GLNG', 'GLPG', 'GLPI', 'GLUU', 'GLYC', 'GNTX', 'GO', 'GOGL', 'GOOD', 'GOOG', 'GOOGL', 'GOSS', 'GRBK', 'GRFS', 'GRMN', 'GSBC', 'GSHD', 'GSM', 'GT', 'GTLS', 'GTYH', 'GWPH', 'HAIN', 'HALO', 'HAS', 'HBAN', 'HBMD', 'HCAT', 'HCM', 'HCSG', 'HDS', 'HELE', 'HFFG', 'HLIO', 'HLNE', 'HMST', 'HMSY', 'HOLX', 'HOMB', 'HONE', 'HOPE', 'HQY', 'HRMY', 'HRTX', 'HSIC', 'HSKA', 'HST', 'HTHT', 'HTLD', 'HTLF', 'HUBG', 'HURN', 'HWC', 'HZNP', 'IAC', 'IART', 'IBKR', 'IBOC', 'IBTX', 'ICFI', 'ICLR', 'ICPT', 'ICUI', 'IDCC', 'IDXX', 'IEP', 'IGMS', 'IIVI', 'ILMN', 'ILPT', 'IMVT', 'INBK', 'INCY', 'INDB', 'INFN', 'INMD', 'INO', 'INOV', 'INSM', 'INTC', 'INTU', 'INVA', 'IONS', 'IOSP', 'IOVA', 'IPAR', 'IPGP', 'IPHI', 'IQ', 'IRBT', 'IRDM', 'IRTC', 'IRWD', 'ISBC', 'ISRG', 'ISTR', 'ITCI', 'ITOS', 'ITRI', 'ITRN', 'JACK', 'JAZZ', 'JBHT', 'JBLU', 'JCOM', 'JD', 'JJSF', 'JKHY', 'JOBS', 'JRVR', 'KALU', 'KALV', 'KBAL', 'KC', 'KDP', 'KELYA', 'KHC', 'KIDS', 'KLAC', 'KLIC', 'KNSL', 'KOD', 'KOPN', 'KPTI', 'KRNT', 'KRNY', 'KRON', 'KROS', 'KRTX', 'KRYS', 'KTOS', 'KURA', 'KYMR', 'LAMR', 'LANC', 'LAUR', 'LBAI', 'LBRDA', 'LBRDK', 'LBTYA', 'LBTYK', 'LECO', 'LESL', 'LFUS', 'LGIH', 'LGND', 'LHCG', 'LI', 'LILAK', 'LITE', 'LIVN', 'LKCO', 'LKFN', 'LKQ', 'LMNX', 'LNT', 'LOB', 'LOGI', 'LOOP', 'LOPE', 'LPLA', 'LPRO', 'LPSN', 'LRCX', 'LSCC', 'LSTR', 'LSXMA', 'LSXMK', 'LULU', 'LUNG', 'LYFT', 'MANH', 'MANT', 'MAR', 'MASI', 'MAT', 'MBUU', 'MCHP', 'MCRB', 'MCRI', 'MDB', 'MDGL', 'MDLZ', 'MDRX', 'MEDP', 'MELI', 'MEOH', 'MERC', 'MGEE', 'MGIC', 'MGLN', 'MGNX', 'MGPI', 'MGRC', 'MIDD', 'MIME', 'MKSI', 'MKTX', 'MLAB', 'MLCO', 'MLHR', 'MMSI', 'MMYT', 'MNRO', 'MNST', 'MOMO', 'MORN', 'MPB', 'MPWR', 'MRCY', 'MRKR', 'MRNA', 'MRSN', 'MRTN', 'MRTX', 'MRVI', 'MRVL', 'MSEX', 'MSFT', 'MSTR', 'MTCH', 'MTSI', 'MU', 'MXIM', 'MYGN', 'NARI', 'NATI', 'NAVI', 'NBIX', 'NBTB', 'NCNA', 'NCNO', 'NDAQ', 'NDSN', 'NEO', 'NEOG', 'NESR', 'NFBK', 'NFE', 'NFLX', 'NGHC', 'NICE', 'NKLA', 'NKTR', 'NKTX', 'NLOK', 'NMIH', 'NNOX', 'NOVT', 'NRC', 'NRIX', 'NSIT', 'NSTG', 'NTAP', 'NTCT', 'NTES', 'NTGR', 'NTLA', 'NTNX', 'NTRA', 'NTRS', 'NUAN', 'NUVA', 'NVAX', 'NVCR', 'NVDA', 'NVMI', 'NWBI', 'NWE', 'NWL', 'NWLI', 'NWS', 'NWSA', 'NXGN', 'NXPI', 'NXST', 'NYMT', 'OAS', 'OCFC', 'ODFL', 'ODP', 'OFLX', 'OKTA', 'OLED', 'OLLI', 'OLMA', 'OM', 'OMCL', 'ON', 'ONB', 'ONEM', 'OPCH', 'OPK', 'ORGO', 'ORLY', 'OSIS', 'OSTK', 'OTEX', 'OTTR', 'OZK', 'PAAS', 'PACB', 'PACW', 'PATK', 'PAYX', 'PBCT', 'PCAR', 'PCH', 'PCRX', 'PCTY', 'PCVX', 'PDCE', 'PDCO', 'PDD', 'PEGA', 'PENN', 'PEP', 'PFBC', 'PFG', 'PFIS', 'PFPT', 'PGNY', 'PINC', 'PLMR', 'PLUG', 'PLUS', 'PLXS', 'PLYA', 'PMVP', 'PNFP', 'PNTG', 'PODD', 'POOL', 'POWI', 'PPBI', 'PPC', 'PPD', 'PRAA', 'PRAH', 'PRDO', 'PRFT', 'PRGS', 'PRIM', 'PRLD', 'PRPL', 'PRQR', 'PRSC', 'PS', 'PSMT', 'PTC', 'PTCT', 'PTON', 'PTVE', 'PYPL', 'PZZA', 'QCOM', 'QDEL', 'QFIN', 'QLYS', 'QNST', 'QRTEA', 'QRVO', 'QTRX', 'QURE', 'RARE', 'RAVN', 'RBCAA', 'RCII', 'RCKT', 'RCM', 'RDFN', 'RDWR', 'REAL', 'REG', 'REGI', 'REGN', 'REPL', 'RETA', 'REYN', 'RGEN', 'RGLD', 'RGNX', 'RLAY', 'RMBS', 'RMR', 'RNA', 'RNST', 'ROCK', 'ROIC', 'ROKU', 'ROLL', 'ROST', 'RP', 'RPD', 'RPRX', 'RRR', 'RUBY', 'RUN', 'RUSHA', 'RVMD', 'RXT', 'RYAAY', 'RYTM', 'SABR', 'SAFM', 'SAFT', 'SAGE', 'SAIA', 'SANM', 'SASR', 'SATS', 'SBAC', 'SBCF', 'SBGI', 'SBLK', 'SBNY', 'SBRA', 'SBSI', 'SBUX', 'SCHL', 'SCOR', 'SCSC', 'SDC', 'SDGR', 'SEDG', 'SEIC', 'SFBS', 'SFIX', 'SFM', 'SFNC', 'SGEN', 'SGMO', 'SGMS', 'SGRY', 'SHC', 'SHEN', 'SHOO', 'SIGI', 'SILK', 'SIMO', 'SINA', 'SIRI', 'SITM', 'SIVB', 'SKYW', 'SLAB', 'SLDB', 'SLGN', 'SLM', 'SLS', 'SMCI', 'SMPL', 'SMTC', 'SNBR', 'SND', 'SNPS', 'SNY', 'SONO', 'SPLK', 'SPNS', 'SPSC', 'SPT', 'SPWR', 'SQBG', 'SRCE', 'SRCL', 'SRNE', 'SRPT', 'SSB', 'SSNC', 'SSRM', 'STAA', 'STAY', 'STBA', 'STFC', 'STLD', 'STMP', 'STNE', 'STRA', 'STX', 'SUMO', 'SUPN', 'SVC', 'SVMK', 'SVRA', 'SWAV', 'SWKS', 'SWTX', 'SYBT', 'SYBX', 'SYKE', 'SYNA', 'SYNH', 'TBIO', 'TBPH', 'TCBI', 'TCBK', 'TCF', 'TCOM', 'TCX', 'TEAM', 'TECH', 'TENB', 'TER', 'TFSL', 'TGTX', 'THFF', 'THRM', 'TIGO', 'TLND', 'TLS', 'TMUS', 'TNDM', 'TOWN', 'TPIC', 'TPTX', 'TREE', 'TRHC', 'TRIP', 'TRMB', 'TRMK', 'TROW', 'TRS', 'TRST', 'TRUP', 'TSCO', 'TSEM', 'TSLA', 'TTD', 'TTEC', 'TTEK', 'TTGT', 'TTMI', 'TTWO', 'TVTX', 'TW', 'TWNK', 'TWOU', 'TWST', 'TXG', 'TXN', 'TXRH', 'UAL', 'UBSI', 'UCBI', 'UEIC', 'UFCS', 'UFPI', 'UHAL', 'UIHC', 'ULH', 'ULTA', 'UMBF', 'UMPQ', 'UNIT', 'UPLD', 'UPWK', 'URBN', 'UTHR', 'UVSP', 'VBTX', 'VC', 'VCYT', 'VEON', 'VG', 'VIAC', 'VIACA', 'VIAV', 'VICR', 'VIE', 'VIR', 'VIRT', 'VITL', 'VLDR', 'VLY', 'VNET', 'VOD', 'VRM', 'VRNS', 'VRNT', 'VRRM', 'VRSK', 'VRSN', 'VRTU', 'VRTX', 'VSAT', 'VTRS', 'WABC', 'WAFD', 'WASH', 'WB', 'WBA', 'WDAY', 'WDC', 'WDFC', 'WEN', 'WERN', 'WING', 'WIRE', 'WIX', 'WKHS', 'WLTW', 'WMG', 'WSBC', 'WSC', 'WSFS', 'WTFC', 'WW', 'WWD', 'WYNN', 'XCUR', 'XEL', 'XLNX', 'XLRN', 'XNCR', 'XP', 'XPER', 'XRAY', 'YMAB', 'YNDX', 'YY', 'Z', 'ZBRA', 'ZG', 'ZGNX', 'ZI', 'ZION', 'ZLAB', 'ZM'],
                     'Others': ['JWN','KSS','HMC','BRK-A','PROG','DS']}

# Note: there are 138 industries, and their names are unique
subgroup_group_dict = {'All': [],
                       'Basic Materials': ['Specialty Chemicals','Chemicals','Agricultural Inputs','Building Materials','Copper','Gold','Other Industrial Metals & Mining','Aluminum','Paper & Paper Products','Steel','Silver','Lumber & Wood Production',],
                       'Communication Services': ['Telecom Services','Electronic Gaming & Multimedia','Entertainment','Internet Content & Information','Advertising Agencies','Broadcasting','Publishing',],
                       'Consumer Cyclical': ['Specialty Retail','Auto Parts','Packaging & Containers','Furnishings, Fixtures & Appliances','Internet Retail','Auto & Truck Dealerships','Restaurants','Leisure','Personal Services','Travel Services','Apparel Retail','Gambling','Lodging','Apparel Manufacturing','Footwear & Accessories','Residential Construction','Resorts & Casinos','Recreational Vehicles','Auto Manufacturers','Home Improvement Retail','Department Stores','Luxury Goods',],
                       'Consumer Defensive': ['Grocery Stores','Farm Products','Education & Training Services','Beverages—Wineries & Distilleries','Packaged Foods','Beverages—Non-Alcoholic','Household & Personal Products','Food Distribution','Discount Stores','Confectioners','Tobacco','Beverages—Brewers',],
                       'Energy': ['Oil & Gas Midstream','Oil & Gas E&P','Thermal Coal','Oil & Gas Equipment & Services','Oil & Gas Integrated','Oil & Gas Refining & Marketing','Oil & Gas Drilling',],
                       'Financial Services': ['Banks—Regional','Insurance—Diversified','Credit Services','Insurance—Property & Casualty','Insurance—Life','Insurance—Specialty','Insurance Brokers','Asset Management','Banks—Diversified','Financial Data & Stock Exchanges','Mortgage Finance','Capital Markets','Financial Conglomerates','Shell Companies','Insurance—Reinsurance',],
                       'Healthcare': ['Diagnostics & Research','Drug Manufacturers—General','Medical Distribution','Medical Devices','Biotechnology','Health Information Services','Medical Care Facilities','Drug Manufacturers—Specialty & Generic','Healthcare Plans','Medical Instruments & Supplies','Pharmaceutical Retailers',],
                       'Industrials': ['Airlines','Building Products & Equipment','Airports & Air Services','Aerospace & Defense','Engineering & Construction','Staffing & Employment Services','Security & Protection Services','Electrical Equipment & Parts','Farm & Heavy Construction Machinery','Specialty Industrial Machinery','Rental & Leasing Services','Trucking','Integrated Freight & Logistics','Business Equipment & Supplies','Consulting Services','Specialty Business Services','Waste Management','Railroads','Industrial Distribution','Marine Shipping','Conglomerates','Tools & Accessories','Metal Fabrication',],
                       'Real Estate': ['REIT—Residential','REIT—Diversified','REIT—Mortgage','REIT—Specialty','REIT—Hotel & Motel','REIT—Office','Real Estate Services','REIT—Retail','REIT—Industrial','REIT—Healthcare Facilities','Real Estate—Diversified',],
                       'Technology': ['Consumer Electronics','Communication Equipment','Software—Infrastructure','Semiconductor Equipment & Materials','Information Technology Services','Semiconductors','Software—Application','Computer Hardware','Electronic Components','Solar','Electronics & Computer Distribution','Scientific & Technical Instruments',],
                       'Utilities': ['Utilities—Regulated Electric','Utilities—Diversified','Utilities—Regulated Gas','Utilities—Regulated Water','Utilities—Renewable','Utilities—Independent Power Producers',],}

# this one is fixed for now (but can be re-generated by find_value_stock() if ticker_group_dict is substantially modified)
# Note: there are 138 industries, and their names are unique
ticker_subgroup_dict = {'Agricultural Inputs': ['CF','CTVA','FMC','MOS','SMG',],
                        'Aluminum': ['KALU',],
                        'Building Materials': ['EXP','MDU','MLM','VMC',],
                        'Chemicals': ['APD','ASH','CE','DD','DOW','EMN','HUN','MEOH','UNVR',],
                        'Copper': ['FCX','SCCO',],
                        'Gold': ['FNV','NEM','RGLD','SSRM',],
                        'Lumber & Wood Production': ['UFPI',],
                        'Other Industrial Metals & Mining': ['GSM',],
                        'Paper & Paper Products': ['MERC',],
                        'Silver': ['PAAS',],
                        'Specialty Chemicals': ['ALB','AVTR','AXTA','BCPC','CBT','CC','ECL','ESI','GRA','IFF','IOSP','LIN','LOOP','LYB','NEU','OLN','PPG','RPM','SHW','WDFC','WLK',],
                        'Steel': ['NUE','RS','STLD',],
                        'Advertising Agencies': ['CMPR','CRTO','IPG','OMC','QNST','SCOR',],
                        'Broadcasting': ['FOX','FOXA','FWONA','FWONK','LSXMA','LSXMK','NWS','NWSA','NXST','SBGI','SIRI',],
                        'Electronic Gaming & Multimedia': ['ATVI','BILI','EA','GLUU','TTWO','ZNGA',],
                        'Entertainment': ['BATRK','CHTR','CMCSA','DIS','DISCA','DISCK','DISH','DLB','LBRDA','LBRDK','LBTYA','LBTYK','LGF-A','LGF-B','LYV','MSGE','MSGS','NFLX','ROKU','VIAC','VIACA','WMG','WWE',],
                        'Internet Content & Information': ['BIDU','CARG','CDLX','FB','GOOG','GOOGL','GRUB','IAC','IQ','LKCO','MOMO','MTCH','NTES','PINS','SINA','SPOT','TTGT','TWLO','TWTR','WB','YNDX','YY','Z','ZG',],
                        'Publishing': ['JW-A','NYT','SCHL',],
                        'Telecom Services': ['ATNI','ATUS','CABO','CCOI','CNSL','GLIBA','IDCC','IRDM','LILAK','LUMN','SHEN','T','TDS','TIGO','TMUS','USM','VEON','VG','VOD','VZ','ZM',],
                        'Apparel Manufacturing': ['COLM','CPRI','HBI','PVH','RL','SQBG','UA','UAA','VFC',],
                        'Apparel Retail': ['BURL','CRI','GPS','LB','LULU','ROST','TJX','URBN',],
                        'Auto & Truck Dealerships': ['AN','KMX','PAG','RUSHA','VRM',],
                        'Auto Manufacturers': ['F','FCAU','GM','HMC','LI','NIO','NKLA','TM','TSLA','WKHS',],
                        'Auto Parts': ['ALSN','APTV','BWA','DORM','GNTX','GT','LEA','LKQ','MNRO','THRM','VC',],
                        'Department Stores': ['JWN','KSS','M',],
                        'Footwear & Accessories': ['CROX','FL','NKE','SHOO','SKX',],
                        'Furnishings, Fixtures & Appliances': ['AMWD','FBHS','KBAL','LEG','MHK','MLHR','SNBR','TPX','WHR',],
                        'Gambling': ['CHDN','DKNG','SGMS',],
                        'Home Improvement Retail': ['FND','HD','LESL','LOW',],
                        'Internet Retail': ['AMZN','BABA','BZUN','CVNA','EBAY','ETSY','JD','MELI','OSTK','PDD','QRTEA','W',],
                        'Leisure': ['BC','HAS','MAT','PLNT','POOL','PTON','SIX',],
                        'Lodging': ['CHH','H','HLT','HTHT','MAR','STAY','WH','WYND',],
                        'Luxury Goods': ['TIF','TPR',],
                        'Packaging & Containers': ['AMCR','ARD','ATR','BERY','BLL','CCK','GPK','IP','PKG','PTVE','REYN','SEE','SLGN','SON','WRK',],
                        'Personal Services': ['BFAM','FRG','FTDR','HRB','ROL','SCI','TMX','WW',],
                        'Recreational Vehicles': ['DOOO','FOXF','HOG','MBUU','PATK','PII','THO',],
                        'Residential Construction': ['CVCO','DHI','GRBK','LEN','LEN-B','LGIH','NVR','PHM','TOL',],
                        'Resorts & Casinos': ['CZR','GDEN','LVS','MCRI','MGM','MLCO','MTN','PENN','PLYA','RRR','WYNN',],
                        'Restaurants': ['ARMK','BLMN','CAKE','CBRL','CMG','DNKN','DPZ','DRI','JACK','MCD','PZZA','SBUX','TXRH','WEN','WING','YUM','YUMC',],
                        'Specialty Retail': ['AAP','AZO','BBBY','BBY','DKS','EYE','FIVE','FLWS','GPC','ODP','ORLY','REAL','SFIX','TSCO','ULTA','WSM',],
                        'Travel Services': ['BKNG','CCL','EXPE','MMYT','NCLH','RCL','TCOM','TRIP',],
                        'Beverages—Brewers': ['SAM','TAP',],
                        'Beverages—Non-Alcoholic': ['CELH','COKE','FIZZ','KDP','KO','MNST','PEP',],
                        'Beverages—Wineries & Distilleries': ['BF-A','BF-B','STZ',],
                        'Confectioners': ['HSY','MDLZ',],
                        'Discount Stores': ['COST','DG','DLTR','OLLI','PSMT','TGT','WMT',],
                        'Education & Training Services': ['AFYA','ARCE','CHGG','GHC','LAUR','LOPE','PRDO','STRA','TWOU',],
                        'Farm Products': ['ADM','AGFS','BG','CALM','TSN','VITL',],
                        'Food Distribution': ['CORE','HFFG','SYY','USFD',],
                        'Grocery Stores': ['ACI','CASY','GO','KR','SFM',],
                        'Household & Personal Products': ['CHD','CL','CLX','COTY','EL','HELE','IPAR','KMB','NUS','NWL','PG','SPB',],
                        'Packaged Foods': ['BRID','BYND','CAG','CENTA','CPB','CVGW','FLO','FRPT','GIS','HAIN','HLF','HRL','INGR','JJSF','K','KHC','LANC','LW','MGPI','MKC','POST','PPC','SAFM','SJM','SMPL','THS','TWNK',],
                        'Tobacco': ['MO','PM',],
                        'Oil & Gas Drilling': ['HP',],
                        'Oil & Gas E&P': ['APA','CLR','COG','COP','CXO','DVN','EOG','EQT','FANG','HES','MRO','MUR','OXY','PDCE','PE','PXD','WPX','XEC',],
                        'Oil & Gas Equipment & Services': ['BKR','CCLP','FTI','GEOS','HAL','NESR','NOV','SLB','SND',],
                        'Oil & Gas Integrated': ['CVX','NFG','TOT','XOM',],
                        'Oil & Gas Midstream': ['ALTM','AM','BKEP','ETRN','GLNG','KMI','LNG','OKE','TRGP','WMB',],
                        'Oil & Gas Refining & Marketing': ['HFC','MPC','PSX','REGI','VLO','VVV',],
                        'Thermal Coal': ['ARLP',],
                        'Asset Management': ['AMG','AMP','APO','ARES','BEN','BK','BLK','CG','DHIL','EV','HLNE','IVZ','KKR','NTRS','SEIC','STT','TROW',],
                        'Banks—Diversified': ['BAC','C','EWBC','JPM','WFC',],
                        'Banks—Regional': ['ABCB','ALTA','ASB','AUB','BANF','BANR','BDGE','BOH','BOKF','BPFH','BPOP','BRKL','BUSE','CAC','CASH','CATY','CBSH','CFFN','CFG','CFR','CHCO','CMA','CNOB','COLB','CTBI','CVBF','EBC','EBSB','EBTC','EFSC','EGBN','FBNC','FCNCA','FFBC','FFIC','FFIN','FHB','FHN','FIBK','FITB','FLIC','FMAO','FMBI','FNB','FNLC','FRC','FRME','FULT','GABC','GBCI','GSBC','HBAN','HBMD','HMST','HOMB','HONE','HOPE','HTLF','HWC','IBOC','IBTX','INBK','INDB','ISBC','ISTR','KEY','KRNY','LBAI','LKFN','LOB','MPB','MTB','NBTB','NFBK','NWBI','NYCB','OCFC','OZK','PACW','PB','PBCT','PFBC','PFIS','PNC','PNFP','PPBI','RBCAA','RF','RNST','SASR','SBCF','SBNY','SBSI','SFBS','SFNC','SIVB','SNV','SRCE','SSB','STBA','STL','SYBT','TCBI','TCBK','TCF','TFC','TFSL','THFF','TOWN','TRMK','TRST','UBSI','UCBI','UMBF','UMPQ','USB','UVSP','VBTX','VLY','WABC','WAFD','WAL','WASH','WBS','WSBC','WSFS','WTFC','ZION',],
                        'Capital Markets': ['EVR','FOCS','FRHC','FUTU','GS','IBKR','LAZ','LPLA','MKTX','MS','RJF','SCHW','TW','VIRT','XP',],
                        'Credit Services': ['ADS','ALLY','AXP','CACC','COF','DFS','FCFS','MA','NAVI','OMF','PRAA','PYPL','SC','SLM','SYF','V','WU',],
                        'Financial Conglomerates': ['JEF','VOYA',],
                        'Financial Data & Stock Exchanges': ['CBOE','CME','FDS','ICE','MCO','MORN','MSCI','NDAQ','SPGI',],
                        'Insurance Brokers': ['AJG','AON','BRO','CRVL','EHTH','ERIE','FANH','GOCO','MMC','WLTW',],
                        'Insurance—Diversified': ['ACGL','AIG','ANAT','ATH','BRK-A','BRK-B','EQH','ESGR','GSHD','HIG','ORI','PFG',],
                        'Insurance—Life': ['AFL','BHF','GL','LNC','MET','NWLI','PRI','PRU','UNM',],
                        'Insurance—Property & Casualty': ['AFG','ALL','AXS','CB','CINF','CNA','KMPR','KNSL','L','LMND','MCY','MKL','NGHC','NMIH','PGR','PLMR','SAFT','SIGI','STFC','THG','TRV','UFCS','UIHC','WRB','WTM','Y',],
                        'Insurance—Reinsurance': ['RE','RGA','RNR',],
                        'Insurance—Specialty': ['AGO','AIZ','AMSF','FAF','FNF','JRVR','MTG','TRUP',],
                        'Mortgage Finance': ['COOP','ECPG','RKT','TREE',],
                        'Shell Companies': ['LPRO',],
                        'Biotechnology': ['ACAD','ACET','ACRS','ADPT','ADVM','AGIO','AKRO','ALEC','ALKS','ALLK','ALLO','ALNY','ALRN','ALVR','ALXN','ALXO','AMRN','AMTI','APLS','ARCT','ARGX','ARNA','ARVN','ARWR','ASND','ATRA','AUPH','AVRO','AXSM','BBIO','BDTX','BEAM','BLCM','BLI','BLUE','BMRN','BNTX','BPMC','BTAI','CBPO','CCXI','CERS','CHRS','CNST','CORT','CRSP','CRTX','CVAC','CYCN','CYTK','DCPH','DNLI','DRNA','EDIT','EIDX','ELOX','ENTA','EPZM','ESPR','EXEL','EYEG','FATE','FBRX','FGEN','FMTX','FOLD','FPRX','GBT','GLPG','GOSS','HALO','HCM','HRMY','HRTX','ICPT','IGMS','IMVT','INCY','INO','INSM','INVA','IONS','IOVA','ITCI','ITOS','JAZZ','KALV','KOD','KPTI','KRON','KROS','KRTX','KRYS','KURA','KYMR','LGND','MCRB','MDGL','MGNX','MRKR','MRNA','MRSN','MRTX','NBIX','NCNA','NKTR','NKTX','NRIX','NSTG','NTLA','NVAX','PCVX','PMVP','PRLD','PRQR','PTCT','QURE','RARE','RCKT','REGN','REPL','RETA','RGNX','RLAY','RNA','RPRX','RUBY','RVMD','RYTM','SAGE','SGEN','SGMO','SLS','SRNE','SRPT','SVRA','SWTX','SYBX','TBIO','TBPH','TECH','TGTX','TPTX','UTHR','VCYT','VIE','VIR','VRTX','XCUR','XLRN','XNCR','YMAB','ZGNX','ZLAB',],
                        'Diagnostics & Research': ['A','BEAT','CDNA','CRL','DGX','DHR','DXCM','EXAS','GH','HSKA','ICLR','IDXX','ILMN','IQV','LH','MEDP','MTD','MYGN','NEO','NEOG','NRC','NTRA','OPK','PACB','PKI','PRAH','QDEL','QGEN','SYNH','TMO','TWST','WAT',],
                        'Drug Manufacturers—General': ['ABBV','AMGN','AZN','BIIB','BMY','GILD','GRFS','GWPH','HZNP','JNJ','LLY','MRK','NVS','PFE','SNY',],
                        'Drug Manufacturers—Specialty & Generic': ['ACRX','AMPH','APHA','ASRT','ATNX','CRON','CTLT','ELAN','IRWD','ORGO','PCRX','PPD','PRGO','SLDB','SUPN','TLRY','ZTS',],
                        'Health Information Services': ['ACCD','CERN','CHNG','CVET','HCAT','HMSY','HQY','INOV','MDRX','NXGN','OMCL','ONEM','PGNY','PINC','RCM','SDGR','TDOC','TRHC','TXG','VEEV',],
                        'Healthcare Plans': ['ANTM','CI','CNC','CVS','HUM','MGLN','MOH','UNH',],
                        'Medical Care Facilities': ['ACHC','ADUS','AMED','CHE','DVA','EHC','ENSG','HCA','HCSG','LHCG','OPCH','OSH','PNTG','PRSC','SGRY','UHS',],
                        'Medical Devices': ['ABMD','ABT','AHCO','ALGN','AXNX','BIO','BRKR','BSX','CSII','EW','GMED','IART','INMD','KIDS','LIVN','LUNG','MDT','NARI','NNOX','NUVA','OM','PEN','PODD','QTRX','SDC','SILK','SWAV','SYK','TNDM','ZBH',],
                        'Medical Distribution': ['ABC','CAH','HSIC','MCK','PDCO',],
                        'Medical Instruments & Supplies': ['ATRC','ATRI','BAX','BDX','COO','ECOR','HAE','HOLX','HRC','ICUI','IRTC','ISRG','LMNX','MASI','MMSI','NVCR','NVST','RGEN','RMD','STAA','STE','TFX','VAR','WST','XRAY',],
                        'Pharmaceutical Retailers': ['WBA',],
                        'Aerospace & Defense': ['AAXN','AVAV','BA','BWXT','ESLT','HEI','HEI-A','HII','HXL','KTOS','LHX','LMT','MRCY','NOC','RTX','SPCE','SPR','TDG','TXT','WWD',],
                        'Airlines': ['AAL','ALGT','ALK','CPA','DAL','JBLU','LUV','RYAAY','SKYW','UAL',],
                        'Airports & Air Services': ['AAWW','MIC',],
                        'Building Products & Equipment': ['AAON','AWI','AZEK','BECN','BLDR','BMCH','CARR','CSL','CSTE','FRTA','MAS','OC','ROCK','TREX',],
                        'Business Equipment & Supplies': ['AVY',],
                        'Conglomerates': ['IEP','SEB',],
                        'Consulting Services': ['BAH','EFX','EXPO','FCN','FORR','HURN','ICFI','INFO','NLSN','TRU','VRSK',],
                        'Electrical Equipment & Parts': ['AEIS','AYI','EAF','ENR','HUBB','NVT','PLUG','VRT','WIRE',],
                        'Engineering & Construction': ['ACM','AEGN','J','JCI','PRIM','PWR','TTEK',],
                        'Farm & Heavy Construction Machinery': ['AGCO','ASTE','CAT','CMCO','DE','OSK','PCAR',],
                        'Industrial Distribution': ['FAST','GWW','HDS','MSM','WSO',],
                        'Integrated Freight & Logistics': ['ATSG','CHRW','CYRX','EXPD','FDX','FWRD','HUBG','JBHT','LSTR','UPS','XPO',],
                        'Marine Shipping': ['GASS','GOGL','KEX','SBLK',],
                        'Metal Fabrication': ['VMI',],
                        'Railroads': ['CSX','KSU','NSC','TRN','UNP','WAB',],
                        'Rental & Leasing Services': ['AL','CAR','MGRC','R','RCII','UHAL','URI','WSC',],
                        'Security & Protection Services': ['ADT','ALLE','MSA','VRRM',],
                        'Specialty Business Services': ['CASS','CPRT','CTAS','GPN','IAA','KODK',],
                        'Specialty Industrial Machinery': ['AIMC','AME','AOS','BLDP','CFX','CMI','CR','CW','DCI','DOV','EMR','ETN','FELE','FLS','GE','GGG','GNRC','GTES','GTLS','HLIO','HON','HWM','IEX','IR','ITT','ITW','KRNT','LII','MIDD','MMM','NDSN','OFLX','OTIS','PH','PNR','RAVN','RBC','ROK','ROP','TPIC','TRS','TT','XYL',],
                        'Staffing & Employment Services': ['ADP','JOBS','KELYA','MAN','PAYX','RHI','UPWK',],
                        'Tools & Accessories': ['LECO','ROLL','SNA','SWK','TKR','TTC',],
                        'Trucking': ['ARCB','HTLD','KNX','MRTN','ODFL','SAIA','SNDR','ULH','WERN',],
                        'Waste Management': ['CLH','CWST','ECOL','RSG','SRCL','WM',],
                        'REIT—Diversified': ['AFIN','ESRT','GOOD','SRC','STOR','VER','VICI','WPC',],
                        'REIT—Healthcare Facilities': ['CTRE','DHC','HTA','MPW','OHI','PEAK','SBRA','VTR','WELL',],
                        'REIT—Hotel & Motel': ['APLE','HST','PK','SVC',],
                        'REIT—Industrial': ['COLD','CUBE','DRE','EXR','FR','ILPT','LSI','PLD','PSA','REXR',],
                        'REIT—Mortgage': ['AGNC','NLY','NRZ','NYMT','STWD',],
                        'REIT—Office': ['ARE','BDN','BXP','COR','CUZ','DEI','DLR','EQC','HIW','HPP','JBGS','KRC','OFC','PGRE','SLG','VNO',],
                        'REIT—Residential': ['ACC','AMH','AVB','CPT','ELS','EQR','ESS','INVH','MAA','SUI','UDR',],
                        'REIT—Retail': ['BPYU','BRX','EPR','FRT','KIM','NNN','O','REG','ROIC','SPG','TCO','WRI',],
                        'REIT—Specialty': ['AMT','CCI','CONE','EQIX','GLPI','IRM','LAMR','OUT','PCH','RYN','SBAC','UNIT',],
                        'Real Estate Services': ['BPY','CBRE','CIGI','CSGP','EXPI','FSV','JLL','RDFN','RMR',],
                        'Real Estate—Diversified': ['HHC',],
                        'Communication Equipment': ['ACIA','CIEN','COMM','CSCO','ERIC','HPE','INFN','ITRN','JNPR','LITE','MSI','NTGR','SATS','UI','VIAV','VSAT','ZBRA',],
                        'Computer Hardware': ['ANET','CRSR','DELL','HPQ','LOGI','NTAP','PSTG','SMCI','STX','WDC',],
                        'Consumer Electronics': ['AAPL','IRBT','SNE','SONO','UEIC',],
                        'Electronic Components': ['APH','FLEX','GLW','JBL','KOPN','LFUS','OSIS','PLXS','SANM','TEL','TTMI','VICR',],
                        'Electronics & Computer Distribution': ['ARW','AVT','CNXN','SCSC',],
                        'Information Technology Services': ['ACN','BR','CACI','CDW','CLGX','CTSH','DNB','DXC','EPAM','EXLS','FIS','FISV','FLT','G','GDS','IBM','IT','JKHY','LDOS','NCR','NSIT','PRFT','SABR','SAIC','SNX','SWCH','SYKE','TDC','TTEC','VNET','VRTU','XRX',],
                        'Scientific & Technical Instruments': ['CGNX','COHR','FARO','FIT','FLIR','FTV','GRMN','IIVI','ITRI','KEYS','MKSI','MLAB','NOVT','ST','TDY','TRMB','VNT',],
                        'Semiconductor Equipment & Materials': ['ACMR','AMAT','AMBA','ASML','BRKS','CCMP','ENTG','IPGP','KLAC','KLIC','LRCX','NVMI','OLED','TER','XPER',],
                        'Semiconductors': ['ADI','ALGM','AMD','AMKR','AVGO','CREE','CRUS','DIOD','FORM','INTC','IPHI','LSCC','MCHP','MPWR','MRVL','MTSI','MU','MXIM','NVDA','NXPI','ON','ONTO','POWI','QCOM','QRVO','RMBS','SIMO','SITM','SLAB','SMTC','SWKS','SYNA','TSEM','TSM','TXN','XLNX',],
                        'Software—Application': ['ADSK','ALRM','ANSS','APPF','APPS','AVLR','AYX','AZPN','BIGC','BILL','BLKB','BSY','CDAY','CDK','CDNS','CLDR','COUP','CRM','CRNC','CSOD','CTXS','CVLT','DCT','DDOG','DOCU','DOMO','DSGX','DT','EGOV','ESTC','EVBG','FICO','FROG','FSLY','GLOB','GTYH','GWRE','HUBS','INTU','KC','LPSN','LYFT','MANH','MANT','MDLA','MGIC','MSTR','NATI','NCNO','NICE','NOW','NUAN','OTEX','PAYC','PCTY','PD','PEGA','PLUS','PRGS','PS','PTC','RNG','RP','RPD','SHOP','SMAR','SPNS','SPT','SSNC','STMP','STNE','SVMK','TEAM','TTD','TYL','UBER','UPLD','WDAY','WORK','ZEN','ZI',],
                        'Software—Infrastructure': ['ACIW','ADBE','AKAM','ALTR','APPN','BAND','BKI','BL','CHKP','CRWD','CSGS','CYBR','DBX','DOX','EEFT','EPAY','EVOP','FEYE','FFIV','FIVN','FTNT','GDDY','JCOM','MDB','MIME','MSFT','NET','NEWR','NLOK','NTCT','NTNX','OKTA','ORCL','PANW','PFPT','PLAN','QLYS','RDWR','RXT','SNPS','SPLK','SPSC','SQ','SWI','TCX','TENB','TLND','VMW','VRNS','VRNT','VRSN','WEX','WIX','ZS',],
                        'Solar': ['ARRY','CSIQ','ENPH','FSLR','RUN','SEDG','SPWR',],
                        'Utilities—Diversified': ['AES','D','ETR','EXC','FE','MGEE','NWE','OTTR','PEG','SRE',],
                        'Utilities—Independent Power Producers': ['NRG','VST',],
                        'Utilities—Regulated Electric': ['AEE','AEP','AGR','CMS','DTE','DUK','ED','EIX','ES','EVRG','HE','IDA','LNT','NEE','OGE','PCG','PNW','PPL','SO','WEC','XEL',],
                        'Utilities—Regulated Gas': ['ATO','CNP','NFE','NI','UGI',],
                        'Utilities—Regulated Water': ['AWK','MSEX','WTRG',],
                        'Utilities—Renewable': ['AY',],}

# make sure ticker_group_dict has everything
for group in subgroup_group_dict.keys():
    for subgroup in subgroup_group_dict[group]:
        for ticker in ticker_subgroup_dict[subgroup]:
            if not ticker in ticker_group_dict[group]:
                ticker_group_dict[group].append(ticker)

# make the ticker elements unique and sorted in ticker_group_dict
for group in ticker_group_dict.keys():
    ticker_group_dict[group] = sorted(list(set(ticker_group_dict[group])))

ticker_group_dict['All'] = sorted(list(set([item for sublist in ticker_group_dict.values() for item in sublist])))

# make sure subgroup_group_dict is complete
for group in ticker_group_dict.keys():
    if not group in subgroup_group_dict.keys():
        subgroup_group_dict[group] = []

subgroup_group_dict['All'] = sorted(list(set([item for sublist in subgroup_group_dict.values() for item in sublist])))

for group in subgroup_group_dict.keys():
    subgroup_group_dict[group] = sorted(subgroup_group_dict[group])
    subgroup_group_dict[group].insert(0, 'All')

# group_desc_dist
group_desc_dict = {'All': f"All unique tickers/symbols included in this app",
                   'Basic Materials': f"Companies engaged in the discovery, development, and processing of raw materials, which are used across a broad range of sectors and industries.",
                   'Communication Services': f"A broad range of companies that sell phone and internet services via traditional landline, broadband, or wireless.",
                   'Consumer Cyclical': f"A category of stocks that rely heavily on the business cycle and economic conditions.\n\nCompanies in the consumer discretionary sector sell goods and services that are considered non-essential, such as appliances, cars, and entertainment.",
                   'Consumer Defensive': f"A category of corporations whose sales and earnings remain relatively stable during both economic upturns and downturns.\n\nFor example, companies that manufacture food, beverages, household and personal products, packaging, or tobacco. Also includes companies that provide services such as education and training services. Defensive companies tend to make products or services that are essential to consumers.\n\nCompanies that produce and sell items considered essential for everyday use.",
                   'Energy': f"Companies focused on the exploration, production, and marketing of oil, gas, and renewable resources around the world.",
                   'Financial Services': f"Companies that offer services including loans, savings, insurance, payment services, and money management for individuals and firms.",
                   'Healthcare': f"A broad range of companies that sell medical products and services.",
                   'Industrials': f"Companies that produce machinery, equipment, and supplies that are used in construction and manufacturing, as well as providing related services.\n\nThese companies are closely tied to the economy, and their business volume often falls sharply during recessions, though each industrial subsector often performs differently.",
                   'Technology': f"Businesses that sell goods and services in electronics, software, computers, artificial intelligence, and other industries related to information technology (IT).",
                   'Utilities': f"Companies that provide electricity, natural gas, water, sewage, and other services to homes and businesses.",
                   'Real Estate': f"Companies that allow individual investors to buy shares in real estate portfolios that receive income from a variety of properties.",
                   'Dividend Stocks (11/2020)': f"Dividend Stocks (11/2020)",
                   'Growth Stocks (11/2020)': f"Growth Stocks (11/2020)",
                   'ETF / ETN': f"Exchange-traded fund (ETF) is a basket of securities that trade on an exchange. Unlike mutual funds (which only trade once a day after the market closes), ETF is just like a stock and share prices fluctuate all day as the ETF is bought and sold.\n\nExchange-traded note (ETN) is a basket of unsecured debt securities that track an underlying index of securities and trade on a major exchange like a stock.\n\nDifference: Investing ETF is investing in a fund that holds the asset it tracks. That asset may be stocks, bonds, gold or other commodities, or futures contracts. In contrast, ETN is more like a bond. It's an unsecured debt note issued by an institution. If the underwriter (usually a bank) were to go bankrupt, the investor would risk a total default.",
                   'Major Market Indices': f"https://www.investing.com/indices/major-indices",
                   'DOW 30': f"Dow Jones Industrial Average 30 Components",
                   'NASDAQ 100': f"A stock market index made up of 103 equity securities issued by 100 of the largest non-financial companies listed on the Nasdaq stock market.\n\nThe complete index, NASDAQ Composite (COMP), has 2,667 securities as of February 2020.\n\nBecause the index is weighted by market capitalization, the index is rather top-heavy. In fact, the top 10 stocks in the Nasdaq Composite account for one-third of the index’s performance.",
                   'S&P 500': f"A stock market index that measures the stock performance of 500 large companies listed on stock exchanges in the United States.\n\nIndex funds that track the S&P 500 have been recommended as investments by Warren Buffett, Burton Malkiel, and John C. Bogle for investors with long time horizons.",
                   'Russell 1000': f"The Russell 1000 Index, a subset of the Russell 3000 Index, represents the 1000 top companies by market capitalization in the United States.\n\nThe Russell 1000 index comprises approximately 92% of the total market capitalization of all listed stocks in the U.S. equity market and is considered a bellwether index for large-cap investing.\n\nNote: Russell 3000 = Russell 1000 (large cap) + Russell 2000 (small cap)",
                   'NASDAQ Composite': f"https://en.wikipedia.org/wiki/NASDAQ_Composite",
                   'Others': f"Others"}

#########################################################################################################

class Ticker(object):
    def __init__(self, ticker=None, ticker_data_dict=None):
        if ticker is None:
            if ticker_data_dict is None:
                raise ValueError('error')
            else:
                self.ticker_data_dict = ticker_data_dict
        else:
            if ticker_data_dict is None:
                from ._data import get_ticker_data_dict
                self.ticker = ticker
                self.ticker_data_dict = get_ticker_data_dict(ticker=self.ticker)
            else:
                self.ticker_data_dict = ticker_data_dict
                self.ticker = ticker_data_dict['ticker']

        self.ticker_info = self.ticker_data_dict['info']
        self.ticker_history = self.ticker_data_dict['history']
        self.last_date = self.ticker_history['Date'].iloc[-1]
        self.last_close_price = self.ticker_history['Close'].iloc[-1]

    def nearest_actual_date(self, target_date):
        idx = self.ticker_history['Date'].searchsorted(target_date)
        return self.ticker_history['Date'].iloc[idx]

    def close_price_on_date(self, target_date):
        max_idx = len(self.ticker_history) - 1
        idx = min( self.ticker_history['Date'].searchsorted(target_date), max_idx ) # if the date is beyond all available dates, idx could be max_idx+1
        #df = self.ticker_history[self.ticker_history['Date'] == target_date]
        #if len(df) != 1:
        #    raise ValueError('not exactly 1 match here')
        return float(self.ticker_history['Close'].iloc[idx]), self.ticker_history['Date'].iloc[idx]

    def key(self, this_key):
        if this_key in self.ticker_info.keys():
            if self.ticker_info[this_key] is not None:
                return round(self.ticker_info[this_key],7)
        return None

    @property
    def price_target(self):
        if 'price_target' in self.ticker_data_dict.keys():
            return self.ticker_data_dict['price_target']
        else:
            return None

    @property
    def pay_dividends(self):
        dividends_df = self.ticker_data_dict['dividends'].reset_index(level=0)
        if len(dividends_df) == 0:
            return False
        else:
            return True

    @property
    def EV_to_EBITDA(self):
        """
        Enterprise value / EBITDA (earnings before interest, taxes, depreciation, and amortization.)
        The lower the better
        """
        return self.key('enterpriseToEbitda')

    @property
    def forwardPE(self):
        """
        Price-to-earnings ratio = Current market price per share / forwardEps
        """
        return self.key('forwardPE')

    @property
    def trailingPE(self):
        """
        Price-to-earnings ratio = Current market price per share / trailingEps
        """
        return self.key('trailingPE')

    @property
    def PEG_ratio(self):
        """
        forward PE / EPS growth (5 year)
        """
        return self.key('pegRatio')

    @property
    def Eps_growth_rate(self):
        """
        Yahoo! Finance, uses a five-year expected growth rate to calculate the PEG ratio.
        https://www.investopedia.com/terms/p/pegratio.asp
        https://www.nasdaq.com/market-activity/stocks/aapl/price-earnings-peg-ratios
        """
        if self.PEG_ratio is not None and self.forwardPE is not None:
            return round(self.forwardPE / self.PEG_ratio, 7)
        return None

    @property
    def forwardEps(self):
        """
        Earning per share
        """
        return self.key('forwardEps')

    @property
    def trailingEps(self):
        return self.key('trailingEps')

    @property
    def Eps_change_pct(self):
        if self.forwardEps is not None and self.trailingEps is not None:
            EPS_change_pct = 100*(self.forwardEps - self.trailingEps)/abs(self.trailingEps)
            return EPS_change_pct
        return None

    @property
    def prob_Eps_change_pct(self):
        if self.Eps_change_pct is not None:
            return sigmoid(self.Eps_change_pct/100)
        return None