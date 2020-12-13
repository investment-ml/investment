# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0

from ..math_and_stats import sigmoid

import pandas as pd

from datetime import datetime, timedelta, timezone

from os.path import join
import pathlib

# NASDAQ Composite Components:
# https://indexes.nasdaqomx.com/Index/Weighting/COMP -> Export
# 2,892 components as of 12/11/2020
# https://quant.stackexchange.com/questions/1640/where-to-download-list-of-all-common-stocks-traded-on-nyse-nasdaq-and-amex
# ftp.nasdaqtrader.com
# http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs

# Russell 1000, 2000, 3000 Components
# https://www.ftserussell.com/resources/russell-reconstitution (download PDF)
# https://www.adobe.com/acrobat/online/pdf-to-excel.html (PDF to Excel conversion)

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
                     'ETF': ['JETS', 'ONEQ', 'IEMG', 'VTHR', 'IWB', 'IWM', 'IWV', 'IWF', 'VTV', 'SCHD', 'USMV', 'VEA', 'VWO', 'AGG', 'LQD', 'GLD', 'VTI', 'DIA', 'OILU', 'OILD', 'TQQQ', 'SQQQ', 'UDOW', 'SDOW', 'UVXY', 'SVXY', 'KORU', 'YANG', 'YINN', 'QQQ', 'VOO','SPY','IVV','TMF','TMV','TBF','TLT','ESPO','GDX','XLC','XLI','XLF','XLE','XLV','XLB','XLK','XLU','XLP','XLY','XLRE'],
                     'Major Market Indices': ['DIA','SPLG','IVV','VOO','SPY','QQQ','ONEQ','IWM','VTWO','VXX'],
                     'DOW 30': ['GS','WMT','MCD','CRM','DIS','NKE','CAT','TRV','VZ','JPM','IBM','HD','INTC','AAPL','MMM','MSFT','JNJ','CSCO','V','DOW','MRK','PG','AXP','KO','AMGN','HON','UNH','WBA','CVX','BA'],
                     'NASDAQ 100': ['AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMD', 'AMGN', 'AMZN', 'ANSS', 'ASML', 'ATVI', 'AVGO', 'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CDNS', 'CDW', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CPRT', 'CSCO', 'CSX', 'CTAS', 'CTSH', 'CTXS', 'DLTR', 'DOCU', 'DXCM', 'EA', 'EBAY', 'EXC', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX', 'FOXA', 'GILD', 'GOOG', 'GOOGL', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JD', 'KDP', 'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'LULU', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MRNA', 'MSFT', 'MU', 'MXIM', 'NFLX', 'NTES', 'NVDA', 'NXPI', 'ORLY', 'PAYX', 'PCAR', 'PDD', 'PEP', 'PYPL', 'QCOM', 'REGN', 'ROST', 'SBUX', 'SGEN', 'SIRI', 'SNPS', 'SPLK', 'SWKS', 'TCOM', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'ULTA', 'VRSK', 'VRSN', 'VRTX', 'WBA', 'WDAY', 'XEL', 'XLNX', 'ZM'],
                     'S&P 500': ['VOO','SPY','IVV','MMM','ABT','ABBV','ABMD','ACN','ATVI','ADBE','AMD','AAP','AES','AFL','A','APD','AKAM','ALK','ALB','ARE','ALXN','ALGN','ALLE','LNT','ALL','GOOGL','GOOG','MO','AMZN','AMCR','AEE','AAL','AEP','AXP','AIG','AMT','AWK','AMP','ABC','AME','AMGN','APH','ADI','ANSS','ANTM','AON','AOS','APA','AIV','AAPL','AMAT','APTV','ADM','ANET','AJG','AIZ','T','ATO','ADSK','ADP','AZO','AVB','AVY','BKR','BLL','BAC','BK','BAX','BDX','BRK-B','BBY','BIO','BIIB','BLK','BA','BKNG','BWA','BXP','BSX','BMY','AVGO','BR','BF-B','CHRW','COG','CDNS','CPB','COF','CAH','KMX','CCL','CARR','CTLT','CAT','CBOE','CBRE','CDW','CE','CNC','CNP','CERN','CF','SCHW','CHTR','CVX','CMG','CB','CHD','CI','CINF','CTAS','CSCO','C','CFG','CTXS','CLX','CME','CMS','KO','CTSH','CL','CMCSA','CMA','CAG','CXO','COP','ED','STZ','COO','CPRT','GLW','CTVA','COST','CCI','CSX','CMI','CVS','DHI','DHR','DRI','DVA','DE','DAL','XRAY','DVN','DXCM','FANG','DLR','DFS','DISCA','DISCK','DISH','DG','DLTR','D','DPZ','DOV','DOW','DTE','DUK','DRE','DD','DXC','EMN','ETN','EBAY','ECL','EIX','EW','EA','EMR','ETR','EOG','EFX','EQIX','EQR','ESS','EL','ETSY','EVRG','ES','RE','EXC','EXPE','EXPD','EXR','XOM','FFIV','FB','FAST','FRT','FDX','FIS','FITB','FE','FRC','FISV','FLT','FLIR','FLS','FMC','F','FTNT','FTV','FBHS','FOXA','FOX','BEN','FCX','GPS','GRMN','IT','GD','GE','GIS','GM','GPC','GILD','GL','GPN','GS','GWW','HAL','HBI','HIG','HAS','HCA','PEAK','HSIC','HSY','HES','HPE','HLT','HFC','HOLX','HD','HON','HRL','HST','HWM','HPQ','HUM','HBAN','HII','IEX','IDXX','INFO','ITW','ILMN','INCY','IR','INTC','ICE','IBM','IP','IPG','IFF','INTU','ISRG','IVZ','IPGP','IQV','IRM','JKHY','J','JBHT','SJM','JNJ','JCI','JPM','JNPR','KSU','K','KEY','KEYS','KMB','KIM','KMI','KLAC','KHC','KR','LB','LHX','LH','LRCX','LW','LVS','LEG','LDOS','LEN','LLY','LNC','LIN','LYV','LKQ','LMT','L','LOW','LUMN','LYB','MTB','MRO','MPC','MKTX','MAR','MMC','MLM','MAS','MA','MKC','MXIM','MCD','MCK','MDT','MRK','MET','MTD','MGM','MCHP','MU','MSFT','MAA','MHK','TAP','MDLZ','MNST','MCO','MS','MOS','MSI','MSCI','NDAQ','NOV','NTAP','NFLX','NWL','NEM','NWSA','NWS','NEE','NLSN','NKE','NI','NSC','NTRS','NOC','NLOK','NCLH','NRG','NUE','NVDA','NVR','ORLY','OXY','ODFL','OMC','OKE','ORCL','OTIS','PCAR','PKG','PH','PAYX','PAYC','PYPL','PNR','PBCT','PEP','PKI','PRGO','PFE','PM','PSX','PNW','PXD','PNC','POOL','PPG','PPL','PFG','PG','PGR','PLD','PRU','PEG','PSA','PHM','PVH','QRVO','PWR','QCOM','DGX','RL','RJF','RTX','O','REG','REGN','RF','RSG','RMD','RHI','ROK','ROL','ROP','ROST','RCL','SPGI','CRM','SBAC','SLB','STX','SEE','SRE','NOW','SHW','SPG','SWKS','SLG','SNA','SO','LUV','SWK','SBUX','STT','STE','SYK','SIVB','SYF','SNPS','SYY','TMUS','TROW','TTWO','TPR','TGT','TEL','FTI','TDY','TFX','TER','TSLA','TXT','TMO','TIF','TJX','TSCO','TT','TDG','TRV','TFC','TWTR','TYL','TSN','UDR','ULTA','USB','UAA','UA','UNP','UAL','UNH','UPS','URI','UHS','UNM','VLO','VAR','VTR','VTRS','VRSN','VRSK','VZ','VRTX','VFC','VIAC','V','VNT','VNO','VMC','WRB','WAB','WMT','WBA','DIS','WM','WAT','WEC','WFC','WELL','WST','WDC','WU','WRK','WY','WHR','WMB','WLTW','WYNN','XEL','XRX','XLNX','XYL','YUM','ZBRA','ZBH','ZION','ZTS'],
                     'Russell 1000': ['A', 'AAL', 'AAP', 'AAPL', 'AAXN', 'ABBV', 'ABC', 'ABMD', 'ABT', 'ACAD', 'ACC', 'ACGL', 'ACHC', 'ACM', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADPT', 'ADS', 'ADSK', 'ADT', 'AEE', 'AEP', 'AES', 'AFG', 'AFL', 'AGCO', 'AGIO', 'AGNC', 'AGO', 'AGR', 'AIG', 'AIV', 'AIZ', 'AJG', 'AKAM', 'AL', 'ALB', 'ALGN', 'ALK', 'ALKS', 'ALL', 'ALLE', 'ALLY', 'ALNY', 'ALSN', 'ALXN', 'AM', 'AMAT', 'AMCR', 'AMD', 'AME', 'AMED', 'AMG', 'AMGN', 'AMH', 'AMP', 'AMT', 'AMTD', 'AMZN', 'AN', 'ANAT', 'ANET', 'ANSS', 'ANTM', 'AON', 'AOS', 'APA', 'APD', 'APH', 'APLE', 'APO', 'APTV', 'ARD', 'ARE', 'ARES', 'ARMK', 'ARW', 'ASB', 'ASH', 'ATH', 'ATO', 'ATR', 'ATUS', 'ATVI', 'AVB', 'AVGO', 'AVLR', 'AVT', 'AVTR', 'AVY', 'AWI', 'AWK', 'AXP', 'AXS', 'AXTA', 'AYI', 'AYX', 'AZO', 'AZPN', 'BA', 'BAC', 'BAH', 'BAX', 'BBY', 'BC', 'BDN', 'BDX', 'BEN', 'BERY', 'BF-A', 'BF-B', 'BFAM', 'BG', 'BHF', 'BIIB', 'BILL', 'BIO', 'BK', 'BKI', 'BKNG', 'BKR', 'BLK', 'BLL', 'BLUE', 'BMRN', 'BMY', 'BOH', 'BOKF', 'BPOP', 'BPYU', 'BR', 'BRK-B', 'BRKR', 'BRO', 'BRX', 'BSX', 'BURL', 'BWA', 'BWXT', 'BXP', 'BYND', 'C', 'CABO', 'CACC', 'CACI', 'CAG', 'CAH', 'CARR', 'CASY', 'CAT', 'CB', 'CBOE', 'CBRE', 'CBSH', 'CBT', 'CC', 'CCI', 'CCK', 'CCL', 'CDAY', 'CDK', 'CDNS', 'CDW', 'CE', 'CERN', 'CF', 'CFG', 'CFR', 'CFX', 'CG', 'CGNX', 'CHD', 'CHE', 'CHGG', 'CHH', 'CHNG', 'CHRW', 'CHTR', 'CI', 'CIEN', 'CINF', 'CL', 'CLGX', 'CLH', 'CLR', 'CLX', 'CMA', 'CMCSA', 'CME', 'CMG', 'CMI', 'CMS', 'CNA', 'CNC', 'CNP', 'COF', 'COG', 'COHR', 'COLD', 'COLM', 'COMM', 'CONE', 'COO', 'COP', 'COR', 'COST', 'COTY', 'COUP', 'CPA', 'CPB', 'CPRI', 'CPRT', 'CPT', 'CR', 'CREE', 'CRI', 'CRL', 'CRM', 'CRUS', 'CRWD', 'CSCO', 'CSGP', 'CSL', 'CSX', 'CTAS', 'CTL', 'CTLT', 'CTSH', 'CTVA', 'CTXS', 'CUBE', 'CUZ', 'CVNA', 'CVS', 'CVX', 'CW', 'CXO', 'CZR', 'D', 'DAL', 'DBX', 'DCI', 'DD', 'DDOG', 'DE', 'DEI', 'DELL', 'DFS', 'DG', 'DGX', 'DHI', 'DHR', 'DIS', 'DISCA', 'DISCK', 'DISH', 'DKS', 'DLB', 'DLR', 'DLTR', 'DNKN', 'DOCU', 'DOV', 'DOW', 'DOX', 'DPZ', 'DRE', 'DRI', 'DT', 'DTE', 'DUK', 'DVA', 'DVN', 'DXC', 'DXCM', 'EA', 'EAF', 'EBAY', 'ECL', 'ED', 'EEFT', 'EFX', 'EHC', 'EIX', 'EL', 'ELAN', 'ELS', 'EMN', 'EMR', 'ENPH', 'ENR', 'ENTG', 'EOG', 'EPAM', 'EPR', 'EQC', 'EQH', 'EQIX', 'EQR', 'EQT', 'ERIE', 'ES', 'ESI', 'ESRT', 'ESS', 'ESTC', 'ETFC', 'ETN', 'ETR', 'ETRN', 'ETSY', 'EV', 'EVBG', 'EVR', 'EVRG', 'EW', 'EWBC', 'EXAS', 'EXC', 'EXEL', 'EXP', 'EXPD', 'EXPE', 'EXR', 'F', 'FAF', 'FANG', 'FAST', 'FB', 'FBHS', 'FCN', 'FCNCA', 'FCX', 'FDS', 'FDX', 'FE', 'FEYE', 'FFIV', 'FHB', 'FHN', 'FICO', 'FIS', 'FISV', 'FITB', 'FIVE', 'FIVN', 'FL', 'FLIR', 'FLO', 'FLS', 'FLT', 'FMC', 'FNB', 'FND', 'FNF', 'FOX', 'FOXA', 'FR', 'FRC', 'FRT', 'FSLR', 'FSLY', 'FTDR', 'FTNT', 'FTV', 'FWONA', 'FWONK', 'G', 'GBT', 'GD', 'GDDY', 'GE', 'GGG', 'GH', 'GHC', 'GILD', 'GIS', 'GL', 'GLIBA', 'GLOB', 'GLPI', 'GLW', 'GM', 'GMED', 'GNRC', 'GNTX', 'GO', 'GOOG', 'GOOGL', 'GPC', 'GPK', 'GPN', 'GPS', 'GRA', 'GRMN', 'GRUB', 'GS', 'GTES', 'GWRE', 'GWW', 'H', 'HAE', 'HAIN', 'HAL', 'HAS', 'HBAN', 'HBI', 'HCA', 'HD', 'HDS', 'HE', 'HEI', 'HEI-A', 'HES', 'HFC', 'HHC', 'HIG', 'HII', 'HIW', 'HLF', 'HLT', 'HOG', 'HOLX', 'HON', 'HP', 'HPE', 'HPP', 'HPQ', 'HRB', 'HRC', 'HRL', 'HSIC', 'HST', 'HSY', 'HTA', 'HUBB', 'HUBS', 'HUM', 'HUN', 'HWM', 'HXL', 'HZNP', 'IAA', 'IAC', 'IART', 'IBKR', 'IBM', 'ICE', 'ICUI', 'IDA', 'IDXX', 'IEX', 'IFF', 'ILMN', 'IMMU', 'INCY', 'INFO', 'INGR', 'INTC', 'INTU', 'INVH', 'IONS', 'IOVA', 'IP', 'IPG', 'IPGP', 'IPHI', 'IQV', 'IR', 'IRM', 'ISRG', 'IT', 'ITT', 'ITW', 'IVZ', 'J', 'JAZZ', 'JBGS', 'JBHT', 'JBL', 'JBLU', 'JCI', 'JEF', 'JKHY', 'JLL', 'JNJ', 'JNPR', 'JPM', 'JW-A', 'JWN', 'K', 'KDP', 'KEX', 'KEY', 'KEYS', 'KHC', 'KIM', 'KKR', 'KLAC', 'KMB', 'KMI', 'KMPR', 'KMX', 'KNX', 'KO', 'KR', 'KRC', 'KSS', 'KSU', 'L', 'LAMR', 'LAZ', 'LB', 'LBRDA', 'LBRDK', 'LDOS', 'LEA', 'LECO', 'LEG', 'LEN', 'LEN-B', 'LFUS', 'LGF-A', 'LGF-B', 'LH', 'LHX', 'LII', 'LIN', 'LITE', 'LKQ', 'LLY', 'LM', 'LMT', 'LNC', 'LNG', 'LNT', 'LOGM', 'LOPE', 'LOW', 'LPLA', 'LRCX', 'LSI', 'LSTR', 'LSXMA', 'LSXMK', 'LULU', 'LUV', 'LVGO', 'LVS', 'LW', 'LYB', 'LYFT', 'LYV', 'MA', 'MAA', 'MAN', 'MANH', 'MAR', 'MAS', 'MASI', 'MAT', 'MCD', 'MCHP', 'MCK', 'MCO', 'MCY', 'MDB', 'MDLA', 'MDLZ', 'MDT', 'MDU', 'MET', 'MGM', 'MHK', 'MIC', 'MIDD', 'MKC', 'MKL', 'MKSI', 'MKTX', 'MLM', 'MMC', 'MMM', 'MNST', 'MO', 'MOH', 'MORN', 'MOS', 'MPC', 'MPW', 'MPWR', 'MRCY', 'MRK', 'MRNA', 'MRO', 'MRVL', 'MS', 'MSA', 'MSCI', 'MSFT', 'MSGE', 'MSGS', 'MSI', 'MSM', 'MTB', 'MTCH', 'MTD', 'MTG', 'MTN', 'MU', 'MUR', 'MXIM', 'MYL', 'NATI', 'NBIX', 'NBL', 'NCLH', 'NCR', 'NDAQ', 'NDSN', 'NEE', 'NEM', 'NET', 'NEU', 'NEWR', 'NFG', 'NFLX', 'NI', 'NKE', 'NKTR', 'NLOK', 'NLSN', 'NLY', 'NNN', 'NOC', 'NOV', 'NOW', 'NRG', 'NRZ', 'NSC', 'NTAP', 'NTNX', 'NTRS', 'NUAN', 'NUE', 'NUS', 'NVCR', 'NVDA', 'NVR', 'NVST', 'NVT', 'NWL', 'NWS', 'NWSA', 'NXST', 'NYCB', 'NYT', 'O', 'OC', 'ODFL', 'OFC', 'OGE', 'OHI', 'OKE', 'OKTA', 'OLED', 'OLLI', 'OLN', 'OMC', 'OMF', 'ON', 'ORCL', 'ORI', 'ORLY', 'OSK', 'OTIS', 'OUT', 'OXY', 'OZK', 'PACW', 'PAG', 'PANW', 'PAYC', 'PAYX', 'PB', 'PBCT', 'PCAR', 'PCG', 'PCTY', 'PD', 'PE', 'PEAK', 'PEG', 'PEGA', 'PEN', 'PEP', 'PFE', 'PFG', 'PFPT', 'PG', 'PGR', 'PGRE', 'PH', 'PHM', 'PII', 'PINC', 'PINS', 'PK', 'PKG', 'PKI', 'PLAN', 'PLD', 'PLNT', 'PM', 'PNC', 'PNFP', 'PNR', 'PNW', 'PODD', 'POOL', 'POST', 'PPC', 'PPD', 'PPG', 'PPL', 'PRAH', 'PRGO', 'PRI', 'PRU', 'PS', 'PSA', 'PSTG', 'PSX', 'PTC', 'PTON', 'PVH', 'PWR', 'PXD', 'PYPL', 'QCOM', 'QDEL', 'QGEN', 'QRTEA', 'QRVO', 'R', 'RBC', 'RCL', 'RE', 'REG', 'REGN', 'RETA', 'REXR', 'REYN', 'RF', 'RGA', 'RGEN', 'RGLD', 'RHI', 'RJF', 'RL', 'RMD', 'RNG', 'RNR', 'ROK', 'ROKU', 'ROL', 'ROP', 'ROST', 'RP', 'RPM', 'RS', 'RSG', 'RTX', 'RYN', 'SABR', 'SAGE', 'SAIC', 'SAM', 'SATS', 'SBAC', 'SBNY', 'SBUX', 'SC', 'SCCO', 'SCHW', 'SCI', 'SEB', 'SEDG', 'SEE', 'SEIC', 'SERV', 'SFM', 'SGEN', 'SHW', 'SIRI', 'SIVB', 'SIX', 'SJM', 'SKX', 'SLB', 'SLG', 'SLGN', 'SLM', 'SMAR', 'SMG', 'SNA', 'SNDR', 'SNPS', 'SNV', 'SNX', 'SO', 'SON', 'SPB', 'SPCE', 'SPG', 'SPGI', 'SPLK', 'SPOT', 'SPR', 'SQ', 'SRC', 'SRCL', 'SRE', 'SRPT', 'SSNC', 'ST', 'STAY', 'STE', 'STL', 'STLD', 'STNE', 'STOR', 'STT', 'STWD', 'STZ', 'SUI', 'SWCH', 'SWI', 'SWK', 'SWKS', 'SYF', 'SYK', 'SYNH', 'SYY', 'T', 'TAP', 'TCF', 'TCO', 'TDC', 'TDG', 'TDOC', 'TDS', 'TDY', 'TEAM', 'TECH', 'TER', 'TFC', 'TFSL', 'TFX', 'TGT', 'THG', 'THO', 'THS', 'TIF', 'TJX', 'TKR', 'TMO', 'TMUS', 'TNDM', 'TOL', 'TPR', 'TPX', 'TREE', 'TREX', 'TRGP', 'TRIP', 'TRMB', 'TRN', 'TROW', 'TRU', 'TRV', 'TSCO', 'TSLA', 'TSN', 'TT', 'TTC', 'TTD', 'TTWO', 'TW', 'TWLO', 'TWOU', 'TWTR', 'TXG', 'TXN', 'TXT', 'TYL', 'UA', 'UAA', 'UAL', 'UBER', 'UDR', 'UGI', 'UHAL', 'UHS', 'UI', 'ULTA', 'UMPQ', 'UNH', 'UNM', 'UNP', 'UNVR', 'UPS', 'URI', 'USB', 'USFD', 'USM', 'UTHR', 'V', 'VAR', 'VEEV', 'VER', 'VFC', 'VIAC', 'VIACA', 'VICI', 'VIRT', 'VLO', 'VMC', 'VMI', 'VMW', 'VNO', 'VOYA', 'VRSK', 'VRSN', 'VRT', 'VRTX', 'VSAT', 'VST', 'VTR', 'VVV', 'VZ', 'W', 'WAB', 'WAL', 'WAT', 'WBA', 'WBS', 'WDAY', 'WDC', 'WEC', 'WELL', 'WEN', 'WEX', 'WFC', 'WH', 'WHR', 'WLK', 'WLTW', 'WM', 'WMB', 'WMT', 'WORK', 'WPC', 'WPX', 'WRB', 'WRI', 'WRK', 'WSM', 'WSO', 'WST', 'WTFC', 'WTM', 'WTRG', 'WU', 'WWD', 'WWE', 'WY', 'WYND', 'WYNN', 'XEC', 'XEL', 'XLNX', 'XLRN', 'XOM', 'XPO', 'XRAY', 'XRX', 'XYL', 'Y', 'YUM', 'YUMC', 'Z', 'ZBH', 'ZBRA', 'ZEN', 'ZG', 'ZION', 'ZM', 'ZNGA', 'ZS', 'ZTS'],
                     'Russell 2000': ['AA', 'AAN', 'AAOI', 'AAON', 'AAT', 'AAWW', 'ABCB', 'ABEO', 'ABG', 'ABM', 'ABR', 'ABTX', 'AC', 'ACA', 'ACBI', 'ACCO', 'ACEL', 'ACIA', 'ACIW', 'ACLS', 'ACNB', 'ACRE', 'ACRX', 'ACTG', 'ADC', 'ADES', 'ADMA', 'ADNT', 'ADRO', 'ADSW', 'ADTN', 'ADUS', 'ADVM', 'AE', 'AEGN', 'AEIS', 'AEL', 'AEO', 'AERI', 'AFIN', 'AFMD', 'AGEN', 'AGFS', 'AGLE', 'AGM', 'AGRX', 'AGS', 'AGTC', 'AGX', 'AGYS', 'AHCO', 'AHH', 'AI', 'AIMC', 'AIMT', 'AIN', 'AIR', 'AIT', 'AJRD', 'AJX', 'AKBA', 'AKCA', 'AKR', 'AKRO', 'AKTS', 'ALBO', 'ALCO', 'ALE', 'ALEC', 'ALEX', 'ALG', 'ALGT', 'ALLK', 'ALLO', 'ALRM', 'ALRS', 'ALSK', 'ALTG', 'ALTR', 'ALX', 'AMAG', 'AMAL', 'AMBA', 'AMBC', 'AMC', 'AMCX', 'AMEH', 'AMK', 'AMKR', 'AMN', 'AMNB', 'AMOT', 'AMPH', 'AMRC', 'AMRK', 'AMRS', 'AMRX', 'AMSC', 'AMSF', 'AMSWA', 'AMTB', 'AMWD', 'ANAB', 'ANDE', 'ANF', 'ANGO', 'ANH', 'ANIK', 'ANIP', 'AOSL', 'APAM', 'APEI', 'APG', 'APLS', 'APLT', 'APOG', 'APPF', 'APPN', 'APPS', 'APRE', 'APT', 'APTS', 'APTX', 'APYX', 'AQST', 'AQUA', 'AR', 'ARA', 'ARAV', 'ARAY', 'ARCB', 'ARCH', 'ARCT', 'ARDX', 'ARGO', 'ARI', 'ARL', 'ARLO', 'ARNA', 'ARNC', 'AROC', 'AROW', 'ARQT', 'ARR', 'ARTNA', 'ARVN', 'ARWR', 'ASC', 'ASGN', 'ASIX', 'ASMB', 'ASPN', 'ASPS', 'ASPU', 'ASTE', 'ASUR', 'AT', 'ATEC', 'ATEN', 'ATEX', 'ATGE', 'ATHX', 'ATI', 'ATKR', 'ATLC', 'ATLO', 'ATNI', 'ATNX', 'ATOM', 'ATRA', 'ATRC', 'ATRI', 'ATRO', 'ATRS', 'ATSG', 'ATXI', 'AUB', 'AUBN', 'AVA', 'AVAV', 'AVCO', 'AVD', 'AVEO', 'AVID', 'AVNS', 'AVRO', 'AVXL', 'AVYA', 'AWH', 'AWR', 'AX', 'AXDX', 'AXGN', 'AXL', 'AXLA', 'AXNX', 'AXSM', 'AXTI', 'AYTU', 'AZZ', 'B', 'BANC', 'BAND', 'BANF', 'BANR', 'BATRA', 'BATRK', 'BBBY', 'BBCP', 'BBIO', 'BBSI', 'BBX', 'BCBP', 'BCC', 'BCEI', 'BCEL', 'BCLI', 'BCML', 'BCO', 'BCOR', 'BCOV', 'BCPC', 'BCRX', 'BDC', 'BDGE', 'BDSI', 'BDTX', 'BE', 'BEAM', 'BEAT', 'BECN', 'BELFB', 'BFC', 'BFIN', 'BFS', 'BFST', 'BFYT', 'BGCP', 'BGS', 'BGSF', 'BH', 'BH-A', 'BHB', 'BHE', 'BHLB', 'BHVN', 'BIG', 'BIPC', 'BJ', 'BJRI', 'BKD', 'BKE', 'BKH', 'BKU', 'BL', 'BLBD', 'BLD', 'BLDR', 'BLFS', 'BLKB', 'BLMN', 'BLPH', 'BLX', 'BMCH', 'BMI', 'BMRC', 'BMTC', 'BNFT', 'BOCH', 'BOMN', 'BOOM', 'BOOT', 'BOX', 'BPFH', 'BPMC', 'BPRN', 'BRBR', 'BRC', 'BREW', 'BRG', 'BRID', 'BRKL', 'BRKS', 'BRMK', 'BRP', 'BRT', 'BRY', 'BSBK', 'BSGM', 'BSIG', 'BSRR', 'BSTC', 'BSVN', 'BTAI', 'BTU', 'BUSE', 'BV', 'BWB', 'BWFG', 'BXG', 'BXMT', 'BXS', 'BY', 'BYD', 'BYSI', 'BZH', 'CABA', 'CAC', 'CADE', 'CAI', 'CAKE', 'CAL', 'CALA', 'CALB', 'CALM', 'CALX', 'CAMP', 'CAR', 'CARA', 'CARE', 'CARG', 'CARS', 'CASA', 'CASH', 'CASI', 'CASS', 'CATB', 'CATC', 'CATM', 'CATO', 'CATS', 'CATY', 'CBAN', 'CBAY', 'CBB', 'CBFV', 'CBIO', 'CBMG', 'CBNK', 'CBRL', 'CBTX', 'CBU', 'CBZ', 'CCB', 'CCBG', 'CCF', 'CCMP', 'CCNE', 'CCOI', 'CCRN', 'CCS', 'CCXI', 'CDE', 'CDLX', 'CDMO', 'CDNA', 'CDTX', 'CDXC', 'CDXS', 'CDZI', 'CECE', 'CEIX', 'CELH', 'CEMI', 'CENT', 'CENTA', 'CENX', 'CERC', 'CERS', 'CETV', 'CEVA', 'CFB', 'CFFI', 'CFFN', 'CFRX', 'CHCO', 'CHCT', 'CHDN', 'CHEF', 'CHK', 'CHMA', 'CHMG', 'CHMI', 'CHRS', 'CHS', 'CHUY', 'CHX', 'CIA', 'CIM', 'CIO', 'CIR', 'CIT', 'CIVB', 'CIX', 'CIZN', 'CKH', 'CKPT', 'CLAR', 'CLBK', 'CLCT', 'CLDR', 'CLDT', 'CLF', 'CLFD', 'CLI', 'CLNC', 'CLNE', 'CLNY', 'CLPR', 'CLVS', 'CLW', 'CLXT', 'CMBM', 'CMC', 'CMCL', 'CMCO', 'CMCT', 'CMD', 'CMO', 'CMP', 'CMPR', 'CMRE', 'CMRX', 'CMTL', 'CNBKA', 'CNCE', 'CNDT', 'CNK', 'CNMD', 'CNNE', 'CNO', 'CNOB', 'CNR', 'CNS', 'CNSL', 'CNST', 'CNTG', 'CNTY', 'CNX', 'CNXN', 'CODX', 'COFS', 'COHU', 'COKE', 'COLB', 'COLL', 'CONN', 'COOP', 'CORE', 'CORR', 'CORT', 'COWN', 'CPF', 'CPK', 'CPLG', 'CPRX', 'CPS', 'CPSI', 'CRAI', 'CRBP', 'CRC', 'CRD-A', 'CRK', 'CRMD', 'CRMT', 'CRNC', 'CRNX', 'CROX', 'CRS', 'CRTX', 'CRVL', 'CRY', 'CSBR', 'CSGS', 'CSII', 'CSOD', 'CSPR', 'CSTE', 'CSTL', 'CSTR', 'CSV', 'CSWI', 'CTB', 'CTBI', 'CTMX', 'CTO', 'CTRE', 'CTRN', 'CTS', 'CTSO', 'CTT', 'CUB', 'CUBI', 'CUE', 'CURO', 'CUTR', 'CVA', 'CVBF', 'CVCO', 'CVCY', 'CVET', 'CVGW', 'CVI', 'CVLT', 'CVLY', 'CVM', 'CVTI', 'CWBR', 'CWCO', 'CWEN', 'CWEN-A', 'CWH', 'CWK', 'CWST', 'CWT', 'CXP', 'CXW', 'CYBE', 'CYCN', 'CYH', 'CYRX', 'CYTK', 'CZNC', 'DAKT', 'DAN', 'DAR', 'DBCP', 'DBD', 'DBI', 'DCO', 'DCOM', 'DCPH', 'DDD', 'DDS', 'DEA', 'DECK', 'DENN', 'DFIN', 'DGICA', 'DGII', 'DHC', 'DHIL', 'DHT', 'DHX', 'DIN', 'DIOD', 'DJCO', 'DK', 'DLTH', 'DLX', 'DMRC', 'DMTK', 'DNLI', 'DNOW', 'DOC', 'DOMO', 'DOOR', 'DORM', 'DRH', 'DRNA', 'DRQ', 'DRRX', 'DSKE', 'DSPG', 'DSSI', 'DTIL', 'DVAX', 'DX', 'DXPE', 'DY', 'DYAI', 'DZSI', 'EARN', 'EAT', 'EB', 'EBF', 'EBIX', 'EBMT', 'EBS', 'EBSB', 'EBTC', 'ECHO', 'ECOL', 'ECOM', 'ECPG', 'EDIT', 'EE', 'EEX', 'EFC', 'EFSC', 'EGAN', 'EGBN', 'EGHT', 'EGLE', 'EGOV', 'EGP', 'EGRX', 'EHTH', 'EIDX', 'EIG', 'EIGI', 'EIGR', 'ELA', 'ELF', 'ELMD', 'ELOX', 'ELY', 'EME', 'EML', 'ENDP', 'ENOB', 'ENS', 'ENSG', 'ENTA', 'ENV', 'ENVA', 'ENZ', 'EOLS', 'EPAC', 'EPAY', 'EPC', 'EPM', 'EPRT', 'EPZM', 'EQBK', 'ERI', 'ERII', 'EROS', 'ESCA', 'ESE', 'ESGR', 'ESNT', 'ESPR', 'ESQ', 'ESSA', 'ESTE', 'ESXB', 'ETH', 'ETM', 'ETNB', 'ETON', 'EVBN', 'EVC', 'EVER', 'EVFM', 'EVH', 'EVI', 'EVLO', 'EVOP', 'EVRI', 'EVTC', 'EXLS', 'EXPI', 'EXPO', 'EXPR', 'EXTN', 'EXTR', 'EYE', 'EZPW', 'FARM', 'FARO', 'FATE', 'FBC', 'FBIO', 'FBIZ', 'FBK', 'FBM', 'FBMS', 'FBNC', 'FBP', 'FC', 'FCAP', 'FCBC', 'FCBP', 'FCCO', 'FCCY', 'FCEL', 'FCF', 'FCFS', 'FCPT', 'FDBC', 'FDP', 'FELE', 'FENC', 'FF', 'FFBC', 'FFG', 'FFIC', 'FFIN', 'FFWM', 'FGBI', 'FGEN', 'FHI', 'FI', 'FIBK', 'FISI', 'FIT', 'FIX', 'FIXX', 'FIZZ', 'FLDM', 'FLGT', 'FLIC', 'FLMN', 'FLNT', 'FLOW', 'FLR', 'FLWS', 'FLXN', 'FMAO', 'FMBH', 'FMBI', 'FMNB', 'FN', 'FNCB', 'FNHC', 'FNKO', 'FNLC', 'FNWB', 'FOCS', 'FOE', 'FOLD', 'FONR', 'FOR', 'FORM', 'FORR', 'FOSL', 'FOXF', 'FPI', 'FPRX', 'FRAF', 'FRBA', 'FRBK', 'FREQ', 'FRG', 'FRGI', 'FRME', 'FRO', 'FRPH', 'FRPT', 'FRTA', 'FSB', 'FSBW', 'FSCT', 'FSFG', 'FSP', 'FSS', 'FSTR', 'FUL', 'FULC', 'FULT', 'FUNC', 'FVCB', 'FVE', 'FWRD', 'GABC', 'GAIA', 'GALT', 'GAN', 'GATX', 'GBCI', 'GBL', 'GBLI', 'GBX', 'GCAP', 'GCBC', 'GCI', 'GCO', 'GCP', 'GDEN', 'GDOT', 'GDP', 'GDYN', 'GEF', 'GEF-B', 'GENC', 'GEO', 'GERN', 'GES', 'GFF', 'GFN', 'GHL', 'GHM', 'GIII', 'GKOS', 'GLDD', 'GLNG', 'GLRE', 'GLT', 'GLUU', 'GLYC', 'GME', 'GMRE', 'GMS', 'GNE', 'GNK', 'GNL', 'GNLN', 'GNMK', 'GNPX', 'GNSS', 'GNTY', 'GNW', 'GOGO', 'GOLF', 'GOOD', 'GORO', 'GOSS', 'GPI', 'GPMT', 'GPOR', 'GPRE', 'GPRO', 'GPX', 'GRBK', 'GRC', 'GRIF', 'GRPN', 'GRTS', 'GRTX', 'GRWG', 'GSB', 'GSBC', 'GSHD', 'GSIT', 'GSKY', 'GT', 'GTHX', 'GTLS', 'GTN', 'GTS', 'GTT', 'GTY', 'GTYH', 'GVA', 'GWB', 'GWGH', 'GWRS', 'HA', 'HAFC', 'HALO', 'HARP', 'HASI', 'HAYN', 'HBB', 'HBCP', 'HBIO', 'HBMD', 'HBNC', 'HBT', 'HCAT', 'HCC', 'HCCI', 'HCHC', 'HCI', 'HCKT', 'HCSG', 'HEAR', 'HEES', 'HELE', 'HFFG', 'HFWA', 'HGV', 'HI', 'HIBB', 'HIFS', 'HL', 'HLI', 'HLIO', 'HLIT', 'HLNE', 'HLX', 'HMHC', 'HMN', 'HMST', 'HMSY', 'HMTV', 'HNGR', 'HNI', 'HOFT', 'HOMB', 'HOME', 'HONE', 'HOOK', 'HOPE', 'HQY', 'HR', 'HRI', 'HROW', 'HRTG', 'HRTX', 'HSC', 'HSII', 'HSKA', 'HSTM', 'HT', 'HTBI', 'HTBK', 'HTH', 'HTLD', 'HTLF', 'HTZ', 'HUBG', 'HUD', 'HURC', 'HURN', 'HVT', 'HWBK', 'HWC', 'HWKN', 'HY', 'HZO', 'IBCP', 'IBIO', 'IBKC', 'IBOC', 'IBP', 'IBTX', 'ICAD', 'ICBK', 'ICFI', 'ICHR', 'ICPT', 'IDCC', 'IDN', 'IDT', 'IDYA', 'IESC', 'IGMS', 'IGT', 'IHC', 'IHRT', 'III', 'IIIN', 'IIIV', 'IIN', 'IIPR', 'IIVI', 'ILPT', 'IMAX', 'IMGN', 'IMKTA', 'IMMR', 'IMRA', 'IMUX', 'IMVT', 'IMXI', 'INBK', 'INDB', 'INFN', 'INFU', 
                                      'INGN', 'INN', 'INO', 'INOV', 'INS', 'INSG', 'INSM', 'INSP', 'INSW', 'INT', 'INTL', 'INVA', 'IOSP', 'IPAR', 'IPI', 'IRBT', 'IRDM', 'IRET', 'IRMD', 'IRT', 'IRTC', 'IRWD', 'ISBC', 'ISEE', 'ISTR', 'ITCI', 'ITGR', 'ITI', 'ITIC', 'ITRI', 'IVAC', 'IVC', 'IVR', 'JACK', 'JBSS', 'JBT', 'JCAP', 'JCOM', 'JELD', 'JJSF', 'JNCE', 'JOE', 'JOUT', 'JRVR', 'JYNT', 'KAI', 'KALA', 'KALU', 'KALV', 'KAMN', 'KAR', 'KBAL', 'KBH', 'KBR', 'KDMN', 'KE', 'KELYA', 'KERN', 'KFRC', 'KFY', 'KIDS', 'KIN', 'KLDO', 'KMT', 'KN', 'KNL', 'KNSA', 'KNSL', 'KOD', 'KODK', 'KOP', 'KOS', 'KPTI', 'KRA', 'KREF', 'KRG', 'KRMD', 'KRNY', 'KRO', 'KROS', 'KRTX', 'KRUS', 'KRYS', 'KTB', 'KTOS', 'KURA', 'KVHI', 'KW', 'KWR', 'KZR', 'LAD', 'LADR', 'LAKE', 'LANC', 'LAND', 'LARK', 'LASR', 'LAUR', 'LAWS', 'LBAI', 'LBC', 'LBRT', 'LC', 'LCI', 'LCII', 'LCNB', 'LCUT', 'LDL', 'LE', 'LEGH', 'LEVL', 'LFVN', 'LGIH', 'LGND', 'LHCG', 'LILA', 'LILAK', 'LIND', 'LIVN', 'LIVX', 'LJPC', 'LKFN', 'LL', 'LLNW', 'LMAT', 'LMNR', 'LMNX', 'LMST', 'LNDC', 'LNN', 'LNTH', 'LOB', 'LOCO', 'LOGC', 'LORL', 'LOVE', 'LPG', 'LPSN', 'LPX', 'LQDA', 'LQDT', 'LRN', 'LSCC', 'LTC', 'LTHM', 'LTRPA', 'LUNA', 'LXFR', 'LXP', 'LXRX', 'LYRA', 'LYTS', 'LZB', 'M', 'MAC', 'MANT', 'MATW', 'MATX', 'MAXR', 'MBCN', 'MBI', 'MBII', 'MBIN', 'MBIO', 'MBUU', 'MBWM', 'MC', 'MCB', 'MCBC', 'MCBS', 'MCF', 'MCFT', 'MCRB', 'MCRI', 'MCS', 'MD', 'MDC', 'MDGL', 'MDP', 'MDRX', 'MEC', 'MED', 'MEDP', 'MEET', 'MEI', 'MEIP', 'MESA', 'MFA', 'MFNC', 'MG', 'MGEE', 'MGI', 'MGLN', 'MGNX', 'MGPI', 'MGRC', 'MGTA', 'MGTX', 'MGY', 'MHH', 'MHO', 'MIK', 'MIME', 'MINI', 'MIRM', 'MITK', 'MJCO', 'MLAB', 'MLHR', 'MLI', 'MLP', 'MLR', 'MLSS', 'MMAC', 'MMI', 'MMS', 'MMSI', 'MNK', 'MNKD', 'MNLO', 'MNOV', 'MNR', 'MNRL', 'MNRO', 'MNSB', 'MNTA', 'MOBL', 'MOD', 'MODN', 'MOFG', 'MOG-A', 'MORF', 'MOV', 'MPAA', 'MPB', 'MPX', 'MR', 'MRBK', 'MRC', 'MRKR', 'MRLN', 'MRNS', 'MRSN', 'MRTN', 'MRTX', 'MSBI', 'MSEX', 'MSGN', 'MSON', 'MSTR', 'MTDR', 'MTEM', 'MTH', 'MTOR', 'MTRN', 'MTRX', 'MTSC', 'MTSI', 'MTW', 'MTX', 'MTZ', 'MUSA', 'MVBF', 'MWA', 'MXL', 'MYE', 'MYFW', 'MYGN', 'MYOK', 'MYRG', 'NAT', 'NATH', 'NATR', 'NAV', 'NAVI', 'NBEV', 'NBHC', 'NBN', 'NBR', 'NBSE', 'NBTB', 'NC', 'NCBS', 'NCMI', 'NDLS', 'NEO', 'NEOG', 'NERV', 'NESR', 'NEX', 'NEXT', 'NFBK', 'NG', 'NGHC', 'NGM', 'NGVC', 'NGVT', 'NH', 'NHC', 'NHI', 'NJR', 'NK', 'NKSH', 'NL', 'NLS', 'NLTX', 'NMIH', 'NMRD', 'NMRK', 'NNBR', 'NNI', 'NODK', 'NOVA', 'NOVT', 'NP', 'NPK', 'NPO', 'NPTN', 'NR', 'NRBO', 'NRC', 'NRIM', 'NSA', 'NSCO', 'NSIT', 'NSP', 'NSSC', 'NSTG', 'NTB', 'NTCT', 'NTGR', 'NTLA', 'NTRA', 'NTUS', 'NUVA', 'NVAX', 'NVEC', 'NVEE', 'NVRO', 'NVTA', 'NWBI', 'NWE', 'NWFL', 'NWLI', 'NWN', 'NWPX', 'NX', 'NXGN', 'NXRT', 'NXTC', 'NYMT', 'NYMX', 'OBNK', 'OCFC', 'OCUL', 'OCX', 'ODC', 'ODP', 'ODT', 'OEC', 'OESX', 'OFED', 'OFG', 'OFIX', 'OFLX', 'OGS', 'OI', 'OII', 'OIS', 'OLP', 'OMCL', 'OMER', 'OMI', 'ONB', 'ONEM', 'ONEW', 'ONTO', 'OOMA', 'OPBK', 'OPCH', 'OPI', 'OPK', 'OPRT', 'OPRX', 'OPTN', 'OPY', 'ORA', 'ORBC', 'ORC', 'ORGO', 'ORGS', 'ORIC', 'ORRF', 'OSBC', 'OSG', 'OSIS', 'OSMT', 'OSPN', 'OSTK', 'OSUR', 'OSW', 'OTTR', 'OVBC', 'OVID', 'OVLY', 'OVV', 'OXM', 'OYST', 'PACB', 'PACK', 'PAE', 'PAHC', 'PANL', 'PAR', 'PARR', 'PASG', 'PATK', 'PAVM', 'PAYS', 'PBF', 'PBFS', 'PBH', 'PBI', 'PBIP', 'PBYI', 'PCB', 'PCH', 'PCRX', 'PCSB', 'PCTI', 'PCYG', 'PCYO', 'PDCE', 'PDCO', 'PDFS', 'PDLB', 'PDLI', 'PDM', 'PEB', 'PEBK', 'PEBO', 'PENN', 'PETQ', 'PETS', 'PFBC', 'PFBI', 'PFC', 'PFGC', 'PFHD', 'PFIS', 'PFNX', 'PFS', 'PFSI', 'PFSW', 'PGC', 'PGEN', 'PGNY', 'PGTI', 'PHAS', 'PHAT', 'PHR', 'PI', 'PICO', 'PINE', 'PING', 'PIPR', 'PIRS', 'PJT', 'PKBK', 'PKE', 'PKOH', 'PLAB', 'PLAY', 'PLBC', 'PLCE', 'PLMR', 'PLOW', 'PLPC', 'PLSE', 'PLT', 'PLUG', 'PLUS', 'PLXS', 'PLYM', 'PMT', 'PNM', 'PNRG', 'PNTG', 'POL', 'POR', 'POWI', 'POWL', 'PPBI', 'PQG', 'PRA', 'PRAA', 'PRDO', 'PRFT', 'PRGS', 'PRIM', 'PRK', 'PRLB', 'PRMW', 'PRNB', 'PRO', 'PROS', 'PROV', 'PRPL', 'PRSC', 'PRSP', 'PRTA', 'PRTH', 'PRTK', 'PRTS', 'PRVB', 'PRVL', 'PSB', 'PSMT', 'PSN', 'PSNL', 'PTCT', 'PTEN', 'PTGX', 'PTLA', 'PTSI', 'PTVCB', 'PUB', 'PUMP', 'PVAC', 'PVBC', 'PWFL', 'PWOD', 'PXLW', 'PZN', 'PZZA', 'QADA', 'QCRH', 'QLYS', 'QMCO', 'QNST', 'QTNT', 'QTRX', 'QTS', 'QTWO', 'QUAD', 'QUOT', 'RAD', 'RAMP', 'RAPT', 'RARE', 'RAVN', 'RBB', 'RBBN', 'RBCAA', 'RBNC', 'RC', 'RCII', 'RCKT', 'RCKY', 'RCM', 'RCUS', 'RDFN', 'RDN', 'RDNT', 'RDUS', 'RDVT', 'REAL', 'REFR', 'REGI', 'REPH', 'REPL', 'RES', 'RESI', 'RESN', 'REV', 'REVG', 'REX', 'REZI', 'RFL', 'RGCO', 'RGNX', 'RGP', 'RGR', 'RGS', 'RH', 'RHP', 'RICK', 'RIG', 'RIGL', 'RILY', 'RLGT', 'RLGY', 'RLI', 'RLJ', 'RLMD', 'RM', 'RMAX', 'RMBI', 'RMBS', 'RMNI', 'RMR', 'RMTI', 'RNST', 'ROAD', 'ROCK', 'ROG', 'ROIC', 'ROLL', 'RPAI', 'RPAY', 'RPD', 'RPT', 'RRBI', 'RRC', 'RRGB', 'RRR', 'RST', 'RTIX', 'RTRX', 'RUBI', 'RUBY', 'RUN', 'RUSHA', 'RUSHB', 'RUTH', 'RVI', 'RVMD', 'RVNC', 'RVP', 'RVSB', 'RWT', 'RXN', 'RYAM', 'RYI', 'RYTM', 'SAFE', 'SAFM', 'SAFT', 'SAH', 'SAIA', 'SAIL', 'SAL', 'SALT', 'SAMG', 'SANM', 'SASR', 'SAVA', 'SAVE', 'SB', 'SBBP', 'SBBX', 'SBCF', 'SBFG', 'SBGI', 'SBH', 'SBRA', 'SBSI', 'SBT', 'SCHL', 'SCHN', 'SCL', 'SCOR', 'SCPH', 'SCS', 'SCSC', 'SCU', 'SCVL', 'SCWX', 'SDGR', 'SEAC', 'SEAS', 'SELB', 'SEM', 'SENEA', 'SF', 'SFBS', 'SFE', 'SFIX', 'SFL', 'SFNC', 'SFST', 'SGA', 'SGC', 'SGH', 'SGMO', 'SGMS', 'SGRY', 'SHAK', 'SHBI', 'SHEN', 'SHO', 'SHOO', 'SHYF', 'SI', 'SIBN', 'SIEB', 'SIEN', 'SIG', 'SIGA', 'SIGI', 'SILK', 'SITC', 'SITE', 'SITM', 'SJI', 'SJW', 'SKT', 'SKY', 'SKYW', 'SLAB', 'SLCA', 'SLCT', 'SLDB', 'SLNO', 'SLP', 'SM', 'SMBC', 'SMBK', 'SMCI', 'SMED', 'SMMF', 'SMP', 'SMPL', 'SMSI', 'SMTC', 'SNBR', 'SNCR', 'SNDX', 'SNFCA', 'SNR', 'SOI', 'SOLY', 'SONA', 'SONO', 'SP', 'SPFI', 'SPKE', 'SPNE', 'SPNS', 'SPOK', 'SPPI', 'SPRO', 'SPSC', 'SPT', 'SPTN', 'SPWH', 'SPWR', 'SPXC', 'SR', 'SRCE', 'SRDX', 'SREV', 'SRG', 'SRI', 'SRNE', 'SRRK', 'SRT', 'SSB', 'SSD', 'SSP', 'SSTI', 'SSTK', 'STAA', 'STAG', 'STAR', 'STBA', 'STC', 'STFC', 'STMP', 'STND', 'STNG', 'STOK', 'STRA', 'STRL', 'STRO', 'STRS', 'STSA', 'STXB', 'STXS', 'SUM', 'SUPN', 'SVC', 'SVMK', 'SVRA', 'SWAV', 'SWBI', 'SWKH', 'SWM', 'SWN', 'SWTX', 'SWX', 'SXC', 'SXI', 'SXT', 'SYBT', 'SYKE', 'SYNA', 'SYRS', 'SYX', 'TACO', 'TALO', 'TARA', 'TAST', 'TBBK', 'TBI', 'TBIO', 'TBK', 'TBNK', 'TBPH', 'TCBI', 'TCBK', 'TCDA', 'TCFC', 'TCI', 'TCMD', 'TCRR', 'TCS', 'TCX', 'TDW', 'TELA', 'TELL', 'TEN', 'TENB', 'TERP', 'TEX', 'TG', 'TGH', 'TGI', 'TGNA', 'TGTX', 'TH', 'THC', 'THFF', 'THR', 'THRM', 'TILE', 'TIPT', 'TISI', 'TITN', 'TLYS', 'TMDX', 'TMHC', 'TMP', 'TMST', 'TNAV', 'TNC', 'TNET', 'TOWN', 'TPB', 'TPC', 'TPCO', 'TPH', 'TPIC', 'TPRE', 'TPTX', 'TR', 'TRC', 'TREC', 'TRHC', 'TRMK', 'TRNO', 'TRNS', 'TROX', 'TRS', 'TRST', 'TRTN', 'TRTX', 'TRUE', 'TRUP', 'TRWH', 'TSBK', 'TSC', 'TSE', 'TTEC', 'TTEK', 'TTGT', 'TTMI', 'TUP', 'TVTY', 'TWNK', 'TWO', 'TWST', 'TXMD', 'TXRH', 'TYME', 'UBA', 'UBFO', 'UBSI', 'UBX', 'UCBI', 'UCTT', 'UE', 'UEC', 'UEIC', 'UFCS', 'UFI', 'UFPI', 'UFPT', 'UFS', 'UHT', 'UIHC', 'UIS', 'ULBI', 'ULH', 'UMBF', 'UMH', 'UNF', 'UNFI', 'UNIT', 'UNTY', 'UPLD', 'UPWK', 'URBN', 'URGN', 'USCR', 'USLM', 'USNA', 'USPH', 'USX', 'UTI', 'UTL', 'UTMD', 'UUUU', 'UVE', 'UVSP', 'UVV', 'VAC', 'VALU', 'VAPO', 'VBIV', 'VBTX', 'VC', 'VCEL', 'VCRA', 'VCYT', 'VEC', 'VECO', 'VERI', 'VERO', 'VERU', 'VERY', 'VG', 'VGR', 'VHC', 'VIAV', 'VICR', 'VIE', 'VIR', 'VIVO', 'VKTX', 'VLGEA', 'VLY', 'VMD', 'VNDA', 'VNRX', 'VOXX', 'VPG', 'VRA', 'VRAY', 'VRCA', 'VREX', 'VRNS', 'VRNT', 'VRRM', 'VRS', 'VRTS', 'VRTU', 'VRTV', 'VSEC', 'VSH', 'VSLR', 'VSTM', 'VSTO', 'VTOL', 'VTVT', 'VVI', 'VVNT', 'VXRT', 'VYGR', 'WABC', 'WAFD', 'WASH', 'WBT', 'WCC', 'WD', 'WDFC', 'WDR', 'WERN', 'WETF', 'WEYS', 'WGO', 'WHD', 'WHG', 'WIFI', 'WINA', 'WING', 'WIRE', 'WK', 'WKHS', 'WLDN', 'WLFC', 'WLL', 'WMC', 'WMGI', 'WMK', 'WMS', 'WNC', 'WNEB', 'WOR', 'WOW', 'WRE', 'WRLD', 'WRTC', 'WSBC', 'WSBF', 'WSC', 'WSFS', 'WSR', 'WTBA', 'WTI', 'WTRE', 'WTRH', 'WTS', 'WTTR', 'WVE', 'WW', 'WWW', 'X', 'XAIR', 'XBIT', 'XCUR', 'XENT', 'XERS', 'XFOR', 'XGN', 'XHR', 'XNCR', 'XOMA', 'XONE', 'XPEL', 'XPER', 'YELP', 'YETI', 'YEXT', 'YMAB', 'YORW', 'ZEUS', 'ZGNX', 'ZIOP', 'ZIXI', 'ZNTL', 'ZUMZ', 'ZUO', 'ZYXI',],
                     'Russell 3000': [],
                     'NASDAQ Composite': ['AACG', 'AACQ', 'AAL', 'AAME', 'AAOI', 'AAON', 'AAPL', 'AAWW', 'AAXN', 'ABCB', 'ABCM', 'ABEO', 'ABIO', 'ABMD', 'ABNB', 'ABST', 'ABTX', 'ABUS', 'ACAD', 'ACAM', 'ACBI', 'ACCD', 'ACER', 'ACET', 'ACEV', 'ACGL', 'ACHC', 'ACHV', 'ACIA', 'ACIU', 'ACIW', 'ACLS', 'ACMR', 'ACNB', 'ACOR', 'ACRS', 'ACRX', 'ACST', 'ACTC', 'ACTG', 'ADAP', 'ADBE', 'ADES', 'ADI', 'ADIL', 'ADMA', 'ADMP', 'ADMS', 'ADOC', 'ADP', 'ADPT', 'ADSK', 'ADTN', 'ADTX', 'ADUS', 'ADV', 'ADVM', 'ADXN', 'ADXS', 'AEGN', 'AEHL', 'AEHR', 'AEIS', 'AEMD', 'AEP', 'AERI', 'AESE', 'AEY', 'AEYE', 'AEZS', 'AFIB', 'AFIN', 'AFMD', 'AFYA', 'AGBA', 'AGC', 'AGEN', 'AGFS', 'AGIO', 'AGLE', 'AGMH', 'AGNC', 'AGRX', 'AGTC', 'AGYS', 'AHAC', 'AHCO', 'AHPI', 'AIH', 'AIHS', 'AIKI', 'AIMC', 'AIRG', 'AIRT', 'AKAM', 'AKBA', 'AKER', 'AKRO', 'AKTS', 'AKTX', 'AKU', 'AKUS', 'ALAC', 'ALBO', 'ALCO', 'ALDX', 'ALEC', 'ALGM', 'ALGN', 'ALGS', 'ALGT', 'ALIM', 'ALJJ', 'ALKS', 'ALLK', 'ALLO', 'ALLT', 'ALNA', 'ALNY', 'ALOT', 'ALPN', 'ALRM', 'ALRN', 'ALRS', 'ALSK', 'ALT', 'ALTA', 'ALTM', 'ALTR', 'ALVR', 'ALXN', 'ALXO', 'ALYA', 'AMAL', 'AMAT', 'AMBA', 'AMCI', 'AMCX', 'AMD', 'AMED', 'AMEH', 'AMGN', 'AMHC', 'AMKR', 'AMNB', 'AMOT', 'AMPH', 'AMRB', 'AMRH', 'AMRK', 'AMRN', 'AMRS', 'AMSC', 'AMSF', 'AMST', 'AMSWA', 'AMTB', 'AMTBB', 'AMTI', 'AMTX', 'AMWD', 'AMYT', 'AMZN', 'ANAB', 'ANAT', 'ANCN', 'ANDA', 'ANDE', 'ANGI', 'ANGO', 'ANIK', 'ANIP', 'ANIX', 'ANNX', 'ANPC', 'ANSS', 'ANTE', 'ANY', 'AOSL', 'AOUT', 'APA', 'APDN', 'APEI', 'APEN', 'APHA', 'API', 'APLS', 'APLT', 'APM', 'APOG', 'APOP', 'APPF', 'APPN', 'APPS', 'APRE', 'APTO', 'APTX', 'APVO', 'APWC', 'APXT', 'APYX', 'AQB', 'AQMS', 'AQST', 'ARAV', 'ARAY', 'ARCB', 'ARCE', 'ARCT', 'ARDS', 'ARDX', 'AREC', 'ARGX', 'ARKR', 'ARLP', 'ARNA', 'AROW', 'ARPO', 'ARQT', 'ARRY', 'ARTL', 'ARTNA', 'ARTW', 'ARVN', 'ARWR', 'ARYA', 'ASLN', 'ASMB', 'ASML', 'ASND', 'ASO', 'ASPS', 'ASPU', 'ASRT', 'ASRV', 'ASTC', 'ASTE', 'ASUR', 'ASYS', 'ATAX', 'ATCX', 'ATEC', 'ATEX', 'ATHA', 'ATHE', 'ATHX', 'ATIF', 'ATLC', 'ATLO', 'ATNF', 'ATNI', 'ATNX', 'ATOM', 'ATOS', 'ATRA', 'ATRC', 'ATRI', 'ATRO', 'ATRS', 'ATSG', 'ATVI', 'ATXI', 'AUB', 'AUBN', 'AUDC', 'AUPH', 'AUTL', 'AUTO', 'AUVI', 'AVAV', 'AVCO', 'AVCT', 'AVDL', 'AVEO', 'AVGO', 'AVGR', 'AVID', 'AVIR', 'AVNW', 'AVO', 'AVRO', 'AVT', 'AVXL', 'AWH', 'AWRE', 'AXAS', 'AXDX', 'AXGN', 'AXLA', 'AXNX', 'AXSM', 'AXTI', 'AY', 'AYLA', 'AYRO', 'AYTU', 'AZN', 'AZPN', 'AZRX', 'AZYO', 'BAND', 'BANF', 'BANR', 'BASI', 'BATRA', 'BATRK', 'BBBY', 'BBCP', 'BBGI', 'BBI', 'BBIG', 'BBIO', 'BBQ', 'BBSI', 'BCBP', 'BCDA', 'BCEL', 'BCLI', 'BCML', 'BCOR', 'BCOV', 'BCOW', 'BCPC', 'BCRX', 'BCTG', 'BCYC', 'BDGE', 'BDSI', 'BDSX', 'BDTX', 'BEAM', 'BEAT', 'BECN', 'BEEM', 'BELFA', 'BELFB', 'BFC', 'BFIN', 'BFRA', 'BFST', 'BGCP', 'BGFV', 'BGNE', 'BHAT', 'BHF', 'BHTG', 'BIDU', 'BIGC', 'BIIB', 'BILI', 'BIMI', 'BIOC', 'BIOL', 'BIVI', 'BJRI', 'BKEP', 'BKNG', 'BKSC', 'BKYI', 'BL', 'BLBD', 'BLCM', 'BLCT', 'BLDP', 'BLDR', 'BLFS', 'BLI', 'BLIN', 'BLKB', 'BLMN', 'BLNK', 'BLPH', 'BLRX', 'BLSA', 'BLU', 'BLUE', 'BMCH', 'BMRA', 'BMRC', 'BMRN', 'BMTC', 'BNFT', 'BNGO', 'BNR', 'BNSO', 'BNTC', 'BNTX', 'BOCH', 'BOKF', 'BOMN', 'BOOM', 'BOSC', 'BOTJ', 'BOWX', 'BOXL', 'BPFH', 'BPMC', 'BPOP', 'BPRN', 'BPTH', 'BPY', 'BPYU', 'BRID', 'BRKL', 'BRKR', 'BRKS', 'BRLI', 'BROG', 'BRP', 'BRPA', 'BRQS', 'BRY', 'BSBK', 'BSET', 'BSGM', 'BSQR', 'BSRR', 'BSVN', 'BSY', 'BTAI', 'BTAQ', 'BTBT', 'BTWN', 'BUSE', 'BVXV', 'BWAY', 'BWB', 'BWEN', 'BWFG', 'BWMX', 'BXRX', 'BYFC', 'BYND', 'BYSI', 'BZUN', 'CAAS', 'CABA', 'CAC', 'CACC', 'CAKE', 'CALA', 'CALB', 'CALM', 'CALT', 'CAMP', 'CAMT', 'CAN', 'CAPA', 'CAPR', 'CAR', 'CARA', 'CARE', 'CARG', 'CARV', 'CASA', 'CASH', 'CASI', 'CASS', 'CASY', 'CATB', 'CATC', 'CATM', 'CATY', 'CBAN', 'CBAT', 'CBAY', 'CBFV', 'CBIO', 'CBLI', 'CBMB', 'CBMG', 'CBNK', 'CBPO', 'CBRL', 'CBSH', 'CBTX', 'CCAP', 'CCB', 'CCBG', 'CCCC', 'CCLP', 'CCMP', 'CCNC', 'CCNE', 'CCOI', 'CCRC', 'CCRN', 'CCXI', 'CD', 'CDAK', 'CDEV', 'CDK', 'CDLX', 'CDMO', 'CDNA', 'CDNS', 'CDTX', 'CDW', 'CDXC', 'CDXS', 'CDZI', 'CECE', 'CELC', 'CELH', 'CEMI', 'CENT', 'CENTA', 'CENX', 'CERC', 'CERE', 'CERN', 'CERS', 'CETX', 'CEVA', 'CFB', 'CFBI', 'CFBK', 'CFFI', 'CFFN', 'CFII', 'CFMS', 'CFRX', 'CG', 'CGC', 'CGEN', 'CGIX', 'CGNX', 'CGRO', 'CHCI', 'CHCO', 'CHDN', 'CHEF', 'CHEK', 'CHFS', 'CHKP', 'CHMA', 'CHMG', 'CHNG', 'CHNR', 'CHPM', 'CHRS', 'CHRW', 'CHTR', 'CHUY', 'CIDM', 'CIGI', 'CIH', 'CIIC', 'CINF', 'CIVB', 'CIZN', 'CJJD', 'CKPT', 'CLAR', 'CLBK', 'CLBS', 'CLCT', 'CLDB', 'CLDX', 'CLEU', 'CLFD', 'CLGN', 'CLIR', 'CLLS', 'CLMT', 'CLNE', 'CLPS', 'CLPT', 'CLRB', 'CLRO', 'CLSD', 'CLSK', 'CLSN', 'CLVS', 'CLWT', 'CLXT', 'CMBM', 'CMCO', 'CMCSA', 'CMCT', 'CME', 'CMLF', 'CMLS', 'CMPI', 'CMPR', 'CMPS', 'CMRX', 'CMTL', 'CNBKA', 'CNCE', 'CNDT', 'CNET', 'CNFR', 'CNNB', 'CNOB', 'CNSL', 'CNSP', 'CNST', 'CNTG', 'CNTY', 'CNXC', 'CNXN', 'COCP', 'CODA', 'CODX', 'COFS', 'COGT', 'COHR', 'COHU', 'COKE', 'COLB', 'COLL', 'COLM', 'COMM', 'CONE', 'CONN', 'COOP', 'CORE', 'CORT', 'COST', 'COUP', 'COWN', 'CPAH', 'CPHC', 'CPIX', 'CPLP', 'CPRT', 'CPRX', 'CPSH', 'CPSI', 'CPSS', 'CPST', 'CPTA', 'CRAI', 'CRBP', 'CRDF', 'CREE', 'CREG', 'CRESY', 'CREX', 'CRIS', 'CRMT', 'CRNC', 'CRNT', 'CRNX', 'CRON', 'CROX', 'CRSA', 'CRSP', 'CRSR', 'CRTD', 'CRTO', 'CRTX', 'CRUS', 'CRVL', 'CRVS', 'CRWD', 'CRWS', 'CSBR', 'CSCO', 'CSCW', 'CSGP', 'CSGS', 'CSII', 'CSIQ', 'CSOD', 'CSPI', 'CSSE', 'CSTE', 'CSTL', 'CSTR', 'CSWC', 'CSWI', 'CSX', 'CTAS', 'CTBI', 'CTG', 'CTHR', 'CTIB', 'CTIC', 'CTMX', 'CTRE', 'CTRM', 'CTRN', 'CTSH', 'CTSO', 'CTXR', 'CTXS', 'CUE', 'CURI', 'CUTR', 'CVAC', 'CVBF', 'CVCO', 'CVCY', 'CVET', 'CVGI', 'CVGW', 'CVLB', 'CVLG', 'CVLT', 'CVLY', 'CVV', 'CWBC', 'CWBR', 'CWCO', 'CWST', 'CXDC', 'CXDO', 'CYAD', 'CYAN', 'CYBE', 'CYBR', 'CYCC', 'CYCN', 'CYRN', 'CYRX', 'CYTH', 'CYTK', 'CZNC', 'CZR', 'CZWI', 'DADA', 'DAIO', 'DAKT', 'DARE', 'DBDR', 'DBVT', 'DBX', 'DCBO', 'DCOM', 'DCPH', 'DCT', 'DCTH', 'DDOG', 'DENN', 'DFFN', 'DFHT', 'DFPH', 'DGICA', 'DGICB', 'DGII', 'DGLY', 'DGNS', 'DHC', 'DHIL', 'DIOD', 'DISCA', 'DISCB', 'DISCK', 'DISH', 'DJCO', 'DKNG', 'DLHC', 'DLPN', 'DLTH', 'DLTR', 'DMAC', 'DMLP', 'DMRC', 'DMTK', 'DNKN', 'DNLI', 'DOCU', 'DOGZ', 'DOMO', 'DOOO', 'DORM', 'DOX', 'DOYU', 'DRAD', 'DRIO', 'DRNA', 'DRRX', 'DRTT', 'DSAC', 'DSGX', 'DSKE', 'DSPG', 'DSWL', 'DTEA', 'DTIL', 'DTSS', 'DUO', 'DUOT', 'DVAX', 'DWSN', 'DXCM', 'DXLG', 'DXPE', 'DXYN', 'DYAI', 'DYN', 'DYNT', 'DZSI', 'EA', 'EAR', 'EARS', 'EAST', 'EBAY', 'EBC', 'EBIX', 'EBMT', 'EBON', 'EBSB', 'EBTC', 'ECHO', 'ECOL', 'ECOR', 'ECPG', 'EDAP', 'EDIT', 'EDRY', 'EDSA', 'EDTK', 'EDUC', 'EEFT', 'EFOI', 'EFSC', 'EGAN', 'EGBN', 'EGLE', 'EGOV', 'EGRX', 'EH', 'EHTH', 'EIDX', 'EIGI', 'EIGR', 'EKSO', 'ELOX', 'ELSE', 'ELTK', 'ELYS', 'EMCF', 'EMKR', 'EML', 'ENDP', 'ENG', 'ENLV', 'ENOB', 'ENPH', 'ENSG', 'ENTA', 'ENTG', 'ENTX', 'EOLS', 'EOSE', 'EPAY', 'EPIX', 'EPSN', 'EPZM', 'EQ', 'EQBK', 'EQIX', 'EQOS', 'ERES', 'ERIC', 'ERIE', 'ERII', 'ERYP', 'ESBK', 'ESCA', 'ESEA', 'ESGR', 'ESLT', 'ESPR', 'ESQ', 'ESSA', 'ESSC', 'ESTA', 'ESXB', 'ETAC', 'ETNB', 'ETON', 'ETSY', 'ETTX', 'EVBG', 'EVER', 'EVFM', 'EVGN', 'EVK', 'EVLO', 'EVOK', 'EVOL', 'EVOP', 'EWBC', 'EXAS', 'EXC', 'EXEL', 'EXFO', 'EXLS', 'EXPC', 'EXPD', 'EXPE', 'EXPI', 'EXPO', 'EXTR', 'EYE', 'EYEG', 'EYEN', 'EYES', 'EYPT', 'EZPW', 'FAMI', 'FANG', 'FANH', 'FARM', 'FARO', 'FAST', 'FAT', 'FATE', 'FB', 'FBIO', 'FBIZ', 'FBMS', 'FBNC', 'FBRX', 'FBSS', 'FCAC', 'FCAP', 'FCBC', 'FCBP', 'FCCO', 'FCCY', 'FCEL', 'FCFS', 'FCNCA', 'FDBC', 'FEIM', 'FELE', 'FENC', 'FEYE', 'FFBC', 'FFBW', 'FFHL', 'FFIC', 'FFIN', 'FFIV', 'FFNW', 'FFWM', 'FGBI', 'FGEN', 'FHB', 'FHTX', 'FIBK', 'FIII', 'FISI', 'FISV', 'FITB', 'FIVE', 'FIVN', 'FIXX', 'FIZZ', 'FLDM', 'FLEX', 'FLGT', 'FLIC', 'FLIR', 'FLL', 'FLMN', 'FLNT', 'FLUX', 'FLWS', 'FLXN', 'FLXS', 'FMAO', 'FMBH', 'FMBI', 'FMNB', 'FMTX', 'FNCB', 'FNHC', 'FNKO', 'FNLC', 'FNWB', 'FOCS', 'FOLD', 'FONR', 'FORD', 'FORM', 'FORR', 'FORTY', 'FOSL', 'FOX', 'FOXA', 'FOXF', 'FPAY', 'FPRX', 'FRAF', 'FRAN', 'FRBA', 'FRBK', 'FREE', 'FREQ', 'FRG', 'FRGI', 'FRHC', 'FRLN', 'FRME', 'FROG', 'FRPH', 'FRPT', 'FRSX', 'FRTA', 'FSBW', 'FSDC', 'FSEA', 'FSFG', 'FSLR', 'FSRV', 'FSTR', 'FSTX', 'FSV', 'FTDR', 'FTEK', 'FTFT', 'FTHM', 'FTIV', 'FTNT', 'FTOC', 'FULC', 'FULT', 'FUNC', 'FUSB', 'FUSN', 'FUTU', 'FUV', 'FVAM', 'FVCB', 'FVE', 'FWONA', 'FWONK', 'FWP', 'FWRD', 'FXNC', 'GABC', 'GAIA', 'GALT', 'GAN', 'GASS', 'GBCI', 'GBIO', 'GBLI', 'GBT', 'GCBC', 'GCMG', 'GDEN', 'GDRX', 'GDS', 'GDYN', 'GEC', 'GENC', 'GENE', 'GEOS', 'GERN', 'GEVO', 'GFED', 'GFN', 'GGAL', 'GH', 'GHIV', 'GHSI', 'GIFI', 'GIGM', 'GIII', 'GILD', 'GILT', 'GLBS', 'GLBZ', 'GLDD', 'GLG', 'GLIBA', 'GLMD', 'GLNG', 'GLPG', 'GLPI', 'GLRE', 'GLSI', 'GLTO', 'GLUU', 'GLYC', 'GMAB', 'GMBL', 'GMDA', 'GMLP', 'GNCA', 'GNFT', 'GNLN', 'GNMK', 'GNPX', 'GNRS', 'GNSS', 'GNTX', 'GNTY', 'GNUS', 'GO', 'GOCO', 'GOGL', 'GOGO', 'GOOD', 'GOOG', 'GOOGL', 'GOSS', 'GOVX', 'GP', 'GPP', 'GPRE', 'GPRO', 'GRAY', 'GRBK', 'GRCY', 'GRFS', 'GRIF', 'GRIL', 'GRIN', 'GRMN', 'GRNQ', 'GRNV', 'GROW', 'GRPN', 'GRSV', 'GRTS', 'GRTX', 'GRVY', 'GRWG', 'GSBC', 'GSHD', 'GSIT', 'GSKY', 'GSM', 'GSMG', 'GSUM', 'GT', 'GTEC', 'GTH', 'GTHX', 'GTIM', 'GTLS', 'GTYH', 'GURE', 'GVP', 'GWAC', 'GWGH', 'GWPH', 'GWRS', 'GXGX', 'GYRO', 
                                          'HA', 'HAFC', 'HAIN', 'HALL', 'HALO', 'HAPP', 'HARP', 'HAS', 'HAYN', 'HBAN', 'HBCP', 'HBIO', 'HBMD', 'HBNC', 'HBP', 'HBT', 'HCAC', 'HCAP', 'HCAT', 'HCCI', 'HCDI', 'HCKT', 'HCM', 'HCSG', 'HDS', 'HDSN', 'HEAR', 'HEC', 'HEES', 'HELE', 'HEPA', 'HFBL', 'HFEN', 'HFFG', 'HFWA', 'HGBL', 'HGEN', 'HGSH', 'HHR', 'HIBB', 'HIFS', 'HIHO', 'HIMX', 'HJLI', 'HLG', 'HLIO', 'HLIT', 'HLNE', 'HLXA', 'HMHC', 'HMNF', 'HMST', 'HMSY', 'HMTV', 'HNNA', 'HNRG', 'HOFT', 'HOFV', 'HOL', 'HOLI', 'HOLX', 'HOMB', 'HONE', 'HOOK', 'HOPE', 'HOTH', 'HPK', 'HQI', 'HQY', 'HRMY', 'HROW', 'HRTX', 'HRZN', 'HSAQ', 'HSDT', 'HSIC', 'HSII', 'HSKA', 'HSON', 'HST', 'HSTM', 'HSTO', 'HTBI', 'HTBK', 'HTBX', 'HTGM', 'HTHT', 'HTLD', 'HTLF', 'HTOO', 'HUBG', 'HUGE', 'HUIZ', 'HURC', 'HURN', 'HUSN', 'HVBC', 'HWBK', 'HWC', 'HWCC', 'HWKN', 'HX', 'HYAC', 'HYFM', 'HYMC', 'HYRE', 'HZNP', 'IAC', 'IART', 'IBCP', 'IBEX', 'IBKR', 'IBOC', 'IBTX', 'ICAD', 'ICBK', 'ICCC', 'ICCH', 'ICFI', 'ICHR', 'ICLK', 'ICLR', 'ICMB', 'ICON', 'ICPT', 'ICUI', 'IDCC', 'IDEX', 'IDN', 'IDRA', 'IDXG', 'IDXX', 'IDYA', 'IEA', 'IEC', 'IEP', 'IESC', 'IFMK', 'IFRX', 'IGAC', 'IGIC', 'IGMS', 'IHRT', 'III', 'IIIN', 'IIIV', 'IIN', 'IIVI', 'IKNX', 'ILMN', 'ILPT', 'IMAB', 'IMAC', 'IMBI', 'IMGN', 'IMKTA', 'IMMP', 'IMMR', 'IMNM', 'IMOS', 'IMRA', 'IMRN', 'IMTE', 'IMTX', 'IMUX', 'IMV', 'IMVT', 'IMXI', 'INAQ', 'INBK', 'INBX', 'INCY', 'INDB', 'INFI', 'INFN', 'INGN', 'INM', 'INMB', 'INMD', 'INO', 'INOD', 'INOV', 'INPX', 'INSE', 'INSG', 'INSM', 'INTC', 'INTG', 'INTU', 'INTZ', 'INVA', 'INVE', 'INVO', 'INZY', 'IONS', 'IOSP', 'IOVA', 'IPAR', 'IPDN', 'IPGP', 'IPHA', 'IPHI', 'IPWR', 'IQ', 'IRBT', 'IRCP', 'IRDM', 'IRIX', 'IRMD', 'IROQ', 'IRTC', 'IRWD', 'ISBC', 'ISEE', 'ISIG', 'ISNS', 'ISRG', 'ISSC', 'ISTR', 'ITAC', 'ITCI', 'ITI', 'ITIC', 'ITMR', 'ITOS', 'ITRI', 'ITRM', 'ITRN', 'IVA', 'IVAC', 'IZEA', 'JACK', 'JAGX', 'JAKK', 'JAMF', 'JAN', 'JAZZ', 'JBHT', 'JBLU', 'JBSS', 'JCOM', 'JCS', 'JCTCF', 'JD', 'JFIN', 'JFU', 'JG', 'JJSF', 'JKHY', 'JNCE', 'JOBS', 'JOUT', 'JRJC', 'JRSH', 'JRVR', 'JUPW', 'JVA', 'JYAC', 'JYNT', 'KALA', 'KALU', 'KALV', 'KBAL', 'KBNT', 'KBSF', 'KC', 'KDMN', 'KDNY', 'KDP', 'KE', 'KELYA', 'KELYB', 'KEQU', 'KERN', 'KFFB', 'KFRC', 'KHC', 'KIDS', 'KIN', 'KINS', 'KIRK', 'KLAC', 'KLDO', 'KLIC', 'KLXE', 'KMDA', 'KNDI', 'KNSA', 'KNSL', 'KNTE', 'KOD', 'KOPN', 'KOR', 'KOSS', 'KPTI', 'KRBP', 'KRKR', 'KRMD', 'KRNT', 'KRNY', 'KRON', 'KROS', 'KRTX', 'KRUS', 'KRYS', 'KSMT', 'KSPN', 'KTCC', 'KTOS', 'KTOV', 'KTRA', 'KURA', 'KVHI', 'KXIN', 'KYMR', 'KZIA', 'KZR', 'LACQ', 'LAKE', 'LAMR', 'LANC', 'LAND', 'LARK', 'LASR', 'LATN', 'LAUR', 'LAWS', 'LAZR', 'LAZY', 'LBAI', 'LBC', 'LBRDA', 'LBRDK', 'LBTYA', 'LBTYB', 'LBTYK', 'LCA', 'LCAP', 'LCNB', 'LCUT', 'LCY', 'LE', 'LECO', 'LEDS', 'LEGH', 'LEGN', 'LESL', 'LEVL', 'LFAC', 'LFUS', 'LFVN', 'LGHL', 'LGIH', 'LGND', 'LHCG', 'LI', 'LIFE', 'LILA', 'LILAK', 'LINC', 'LIND', 'LIQT', 'LITE', 'LIVE', 'LIVK', 'LIVN', 'LIVX', 'LIXT', 'LIZI', 'LJPC', 'LKCO', 'LKFN', 'LKQ', 'LLIT', 'LLNW', 'LMAT', 'LMB', 'LMFA', 'LMNL', 'LMNR', 'LMNX', 'LMPX', 'LMRK', 'LMST', 'LNDC', 'LNSR', 'LNT', 'LNTH', 'LOAC', 'LOAN', 'LOB', 'LOCO', 'LOGC', 'LOGI', 'LOOP', 'LOPE', 'LORL', 'LOVE', 'LPCN', 'LPLA', 'LPRO', 'LPSN', 'LPTH', 'LPTX', 'LQDA', 'LQDT', 'LRCX', 'LRMR', 'LSAC', 'LSAQ', 'LSBK', 'LSCC', 'LSTR', 'LSXMA', 'LSXMB', 'LSXMK', 'LTBR', 'LTRN', 'LTRPA', 'LTRPB', 'LTRX', 'LULU', 'LUMO', 'LUNA', 'LUNG', 'LWAY', 'LX', 'LXEH', 'LXRX', 'LYFT', 'LYL', 'LYRA', 'LYTS', 'MAAC', 'MACK', 'MACU', 'MAGS', 'MANH', 'MANT', 'MAR', 'MARA', 'MARK', 'MARPS', 'MASI', 'MAT', 'MATW', 'MAXN', 'MAYS', 'MBCN', 'MBII', 'MBIN', 'MBIO', 'MBOT', 'MBRX', 'MBUU', 'MBWM', 'MCAC', 'MCBC', 'MCBS', 'MCEP', 'MCFE', 'MCFT', 'MCHP', 'MCHX', 'MCMJ', 'MCRB', 'MCRI', 'MDB', 'MDCA', 'MDGL', 'MDGS', 'MDIA', 'MDJH', 'MDLZ', 'MDNA', 'MDRR', 'MDRX', 'MDVL', 'MDWD', 'MDXG', 'MEDP', 'MEDS', 'MEIP', 'MELI', 'MEOH', 'MERC', 'MESA', 'MESO', 'METC', 'METX', 'MFH', 'MFIN', 'MFNC', 'MGEE', 'MGEN', 'MGI', 'MGIC', 'MGLN', 'MGNI', 'MGNX', 'MGPI', 'MGRC', 'MGTA', 'MGTX', 'MGYR', 'MHLD', 'MICT', 'MIDD', 'MIK', 'MIME', 'MIND', 'MIRM', 'MIST', 'MITK', 'MITO', 'MKD', 'MKGI', 'MKSI', 'MKTX', 'MLAB', 'MLAC', 'MLCO', 'MLHR', 'MLND', 'MLVF', 'MMAC', 'MMLP', 'MMSI', 'MMYT', 'MNCL', 'MNDO', 'MNKD', 'MNOV', 'MNPR', 'MNRO', 'MNSB', 'MNST', 'MNTX', 'MOFG', 'MOGO', 'MOHO', 'MOMO', 'MOR', 'MORF', 'MORN', 'MOSY', 'MOTS', 'MOXC', 'MPAA', 'MPB', 'MPWR', 'MRAM', 'MRBK', 'MRCY', 'MREO', 'MRIN', 'MRKR', 'MRLN', 'MRNA', 'MRNS', 'MRSN', 'MRTN', 'MRTX', 'MRUS', 'MRVI', 'MRVL', 'MSBI', 'MSEX', 'MSFT', 'MSON', 'MSTR', 'MSVB', 'MTBC', 'MTC', 'MTCH', 'MTCR', 'MTEM', 'MTEX', 'MTLS', 'MTP', 'MTRX', 'MTSC', 'MTSI', 'MTSL', 'MU', 'MVBF', 'MVIS', 'MWK', 'MXIM', 'MYFW', 'MYGN', 'MYRG', 'MYSZ', 'MYT', 'NAII', 'NAKD', 'NAOV', 'NARI', 'NATH', 'NATI', 'NATR', 'NAVI', 'NBAC', 'NBEV', 'NBIX', 'NBLX', 'NBN', 'NBRV', 'NBSE', 'NBTB', 'NCBS', 'NCMI', 'NCNA', 'NCNO', 'NCSM', 'NCTY', 'NDAQ', 'NDLS', 'NDRA', 'NDSN', 'NEO', 'NEOG', 'NEON', 'NEOS', 'NEPH', 'NEPT', 'NERV', 'NESR', 'NETE', 'NEWA', 'NEWT', 'NEXT', 'NFBK', 'NFE', 'NFLX', 'NGAC', 'NGHC', 'NGM', 'NGMS', 'NH', 'NHIC', 'NHLD', 'NHTC', 'NICE', 'NICK', 'NISN', 'NIU', 'NK', 'NKLA', 'NKSH', 'NKTR', 'NKTX', 'NLOK', 'NLTX', 'NMCI', 'NMFC', 'NMIH', 'NMMC', 'NMRD', 'NMRK', 'NMTR', 'NNBR', 'NNDM', 'NNOX', 'NODK', 'NOVN', 'NOVS', 'NOVT', 'NPA', 'NRBO', 'NRC', 'NRIM', 'NRIX', 'NSEC', 'NSIT', 'NSSC', 'NSTG', 'NSYS', 'NTAP', 'NTCT', 'NTEC', 'NTES', 'NTGR', 'NTIC', 'NTLA', 'NTNX', 'NTRA', 'NTRS', 'NTUS', 'NTWK', 'NUAN', 'NURO', 'NUVA', 'NUZE', 'NVAX', 'NVCN', 'NVCR', 'NVDA', 'NVEC', 'NVEE', 'NVFY', 'NVIV', 'NVMI', 'NVUS', 'NWBI', 'NWE', 'NWFL', 'NWL', 'NWLI', 'NWPX', 'NWS', 'NWSA', 'NXGN', 'NXPI', 'NXST', 'NXTC', 'NXTD', 'NYMT', 'NYMX', 'OAS', 'OBAS', 'OBCI', 'OBLN', 'OBNK', 'OBSV', 'OCC', 'OCFC', 'OCGN', 'OCUL', 'OCUP', 'ODFL', 'ODP', 'ODT', 'OEG', 'OESX', 'OFED', 'OFIX', 'OFLX', 'OGI', 'OIIM', 'OKTA', 'OLB', 'OLED', 'OLLI', 'OLMA', 'OM', 'OMAB', 'OMCL', 'OMER', 'OMEX', 'OMP', 'ON', 'ONB', 'ONCR', 'ONCS', 'ONCT', 'ONCY', 'ONDS', 'ONEM', 'ONEW', 'ONTX', 'ONVO', 'OPBK', 'OPCH', 'OPES', 'OPGN', 'OPHC', 'OPI', 'OPK', 'OPNT', 'OPOF', 'OPRA', 'OPRT', 'OPRX', 'OPT', 'OPTN', 'OPTT', 'ORBC', 'ORGO', 'ORGS', 'ORIC', 'ORLY', 'ORMP', 'ORPH', 'ORRF', 'ORTX', 'OSBC', 'OSIS', 'OSMT', 'OSN', 'OSPN', 'OSS', 'OSTK', 'OSUR', 'OSW', 'OTEL', 'OTEX', 'OTIC', 'OTLK', 'OTRK', 'OTTR', 'OVBC', 'OVID', 'OVLY', 'OXBR', 'OXFD', 'OYST', 'OZK', 'OZON', 'PAAS', 'PACB', 'PACW', 'PAE', 'PAHC', 'PAIC', 'PAND', 'PANL', 'PASG', 'PATI', 'PATK', 'PAVM', 'PAYA', 'PAYS', 'PAYX', 'PBCT', 'PBFS', 'PBHC', 'PBIP', 'PBLA', 'PBPB', 'PBTS', 'PBYI', 'PCAR', 'PCB', 'PCH', 'PCOM', 'PCRX', 'PCSA', 'PCSB', 'PCTI', 'PCTY', 'PCVX', 'PCYG', 'PCYO', 'PDCE', 'PDCO', 'PDD', 'PDEX', 'PDFS', 'PDLB', 'PDLI', 'PDSB', 'PEBK', 'PEBO', 'PECK', 'PEGA', 'PEIX', 'PENN', 'PEP', 'PERI', 'PESI', 'PETQ', 'PETS', 'PETZ', 'PFBC', 'PFBI', 'PFC', 'PFG', 'PFHD', 'PFIE', 'PFIN', 'PFIS', 'PFMT', 'PFPT', 'PFSW', 'PGC', 'PGEN', 'PGNY', 'PHAS', 'PHAT', 'PHCF', 'PHIO', 'PHUN', 'PI', 'PICO', 'PIH', 'PINC', 'PIRS', 'PIXY', 'PKBK', 'PKOH', 'PLAB', 'PLAY', 'PLBC', 'PLCE', 'PLIN', 'PLL', 'PLMR', 'PLPC', 'PLRX', 'PLSE', 'PLUG', 'PLUS', 'PLXP', 'PLXS', 'PLYA', 'PMBC', 'PMD', 'PME', 'PMVP', 'PNBK', 'PNFP', 'PNRG', 'PNTG', 'POAI', 'PODD', 'POLA', 'POOL', 'POWI', 'POWL', 'POWW', 'PPBI', 'PPC', 'PPD', 'PPIH', 'PPSI', 'PRAA', 'PRAH', 'PRAX', 'PRCP', 'PRDO', 'PRFT', 'PRFX', 'PRGS', 'PRGX', 'PRIM', 'PRLD', 'PROF', 'PROG', 'PROV', 'PRPH', 'PRPL', 'PRPO', 'PRQR', 'PRSC', 'PRTA', 'PRTC', 'PRTH', 'PRTK', 'PRTS', 'PRVB', 'PRVL', 'PS', 'PSAC', 'PSHG', 'PSMT', 'PSNL', 'PSTI', 'PSTV', 'PSTX', 'PT', 'PTAC', 'PTC', 'PTCT', 'PTE', 'PTEN', 'PTGX', 'PTI', 'PTNR', 'PTON', 'PTPI', 'PTRS', 'PTSI', 'PTVCA', 'PTVCB', 'PTVE', 'PUBM', 'PULM', 'PUYI', 'PVAC', 'PVBC', 'PWFL', 'PWOD', 'PXLW', 'PXS', 'PYPD', 'PYPL', 'PZZA', 'QADA', 'QADB', 'QCOM', 'QCRH', 'QDEL', 'QELL', 'QFIN', 'QH', 'QIWI', 'QK', 'QLGN', 'QLYS', 'QMCO', 'QNST', 'QRHC', 'QRTEA', 'QRTEB', 'QRVO', 'QTNT', 'QTRX', 'QTT', 'QUIK', 'QUMU', 'QURE', 'RACA', 'RADA', 'RADI', 'RAIL', 'RAPT', 'RARE', 'RAVE', 'RAVN', 'RBB', 'RBBN', 'RBCAA', 'RBCN', 'RBKB', 'RBNC', 'RCEL', 'RCHG', 'RCII', 'RCKT', 'RCKY', 'RCM', 'RCMT', 'RCON', 'RDCM', 'RDFN', 'RDHL', 'RDI', 'RDIB', 'RDNT', 'RDUS', 'RDVT', 'RDWR', 'REAL', 'REDU', 'REED', 'REFR', 'REG', 'REGI', 'REGN', 'REKR', 'RELL', 'RELV', 'REPH', 'REPL', 'RESN', 'RETA', 'RETO', 'REYN', 'RFIL', 'RGCO', 'RGEN', 'RGLD', 'RGLS', 'RGNX', 'RGP', 'RIBT', 'RICK', 'RIDE', 'RIGL', 'RILY', 'RIOT', 'RIVE', 'RKDA', 'RLAY', 'RLMD', 'RMBI', 'RMBL', 'RMBS', 'RMCF', 'RMNI', 'RMR', 'RMTI', 'RNA', 'RNDB', 'RNET', 'RNLX', 'RNST', 'RNWK', 'ROAD', 'ROCH', 'ROCK', 'ROIC', 'ROKU', 'ROLL', 'ROOT', 'ROST', 'RP', 'RPAY', 'RPD', 'RPRX', 'RPTX', 'RRBI', 'RRGB', 'RRR', 'RSSS', 'RTLR', 'RUBY', 'RUHN', 'RUN', 'RUSHA', 'RUSHB', 'RUTH', 'RVMD', 'RVNC', 'RVSB', 'RWLK', 'RXT', 'RYAAY', 'RYTM', 'RZLT', 'SABR', 'SAFM', 'SAFT', 'SAGE', 'SAIA', 'SAII', 'SAL', 'SALM', 'SAMA', 'SAMG', 'SANM', 'SANW', 'SASR', 'SATS', 'SAVA', 'SBAC', 'SBBP', 'SBCF', 'SBFG', 'SBGI', 'SBLK', 'SBNY', 'SBRA', 'SBSI', 'SBT', 'SBTX', 'SBUX', 'SCHL', 'SCHN', 'SCKT', 'SCOR', 'SCPH', 'SCPL', 
                                          'SCSC', 'SCVL', 'SCWX', 'SCYX', 'SDC', 'SDGR', 'SEAC', 'SECO', 'SEDG', 'SEED', 'SEEL', 'SEER', 'SEIC', 'SELB', 'SELF', 'SENEA', 'SENEB', 'SESN', 'SFBC', 'SFBS', 'SFET', 'SFIX', 'SFM', 'SFNC', 'SFST', 'SFT', 'SG', 'SGA', 'SGAM', 'SGBX', 'SGC', 'SGEN', 'SGH', 'SGLB', 'SGMA', 'SGMO', 'SGMS', 'SGOC', 'SGRP', 'SGRY', 'SGTX', 'SHBI', 'SHC', 'SHEN', 'SHIP', 'SHOO', 'SHSP', 'SHYF', 'SIBN', 'SIC', 'SIEB', 'SIEN', 'SIFY', 'SIGA', 'SIGI', 'SILC', 'SILK', 'SIMO', 'SINA', 'SINO', 'SINT', 'SIOX', 'SIRI', 'SITM', 'SIVB', 'SJ', 'SKYW', 'SLAB', 'SLCT', 'SLDB', 'SLGG', 'SLGL', 'SLGN', 'SLM', 'SLN', 'SLNO', 'SLP', 'SLRX', 'SLS', 'SMBC', 'SMBK', 'SMCI', 'SMED', 'SMID', 'SMIT', 'SMMC', 'SMMF', 'SMMT', 'SMPL', 'SMSI', 'SMTC', 'SMTI', 'SMTX', 'SNBR', 'SNCA', 'SNCR', 'SND', 'SNDE', 'SNDL', 'SNDX', 'SNES', 'SNEX', 'SNFCA', 'SNGX', 'SNOA', 'SNPS', 'SNSS', 'SNY', 'SOHO', 'SOHU', 'SOLO', 'SOLY', 'SONA', 'SONM', 'SONN', 'SONO', 'SP', 'SPCB', 'SPFI', 'SPI', 'SPKE', 'SPLK', 'SPNE', 'SPNS', 'SPOK', 'SPPI', 'SPRB', 'SPRO', 'SPRT', 'SPSC', 'SPT', 'SPTN', 'SPWH', 'SPWR', 'SQBG', 'SQFT', 'SRAC', 'SRAX', 'SRCE', 'SRCL', 'SRDX', 'SREV', 'SRGA', 'SRNE', 'SRPT', 'SRRA', 'SRRK', 'SRTS', 'SSB', 'SSBI', 'SSKN', 'SSNC', 'SSNT', 'SSP', 'SSPK', 'SSRM', 'SSTI', 'SSYS', 'STAA', 'STAF', 'STAY', 'STBA', 'STCN', 'STEP', 'STFC', 'STIM', 'STKL', 'STKS', 'STLD', 'STMP', 'STND', 'STNE', 'STOK', 'STRA', 'STRL', 'STRM', 'STRO', 'STRS', 'STRT', 'STSA', 'STTK', 'STWO', 'STX', 'STXB', 'SUMO', 'SUMR', 'SUNW', 'SUPN', 'SURF', 'SV', 'SVA', 'SVAC', 'SVBI', 'SVC', 'SVMK', 'SVRA', 'SWAV', 'SWBI', 'SWIR', 'SWKH', 'SWKS', 'SWTX', 'SXTC', 'SY', 'SYBT', 'SYBX', 'SYKE', 'SYNA', 'SYNC', 'SYNH', 'SYNL', 'SYPR', 'SYRS', 'SYTA', 'TA', 'TACO', 'TACT', 'TAIT', 'TANH', 'TAOP', 'TARA', 'TARS', 'TAST', 'TATT', 'TAYD', 'TBBK', 'TBIO', 'TBK', 'TBLT', 'TBNK', 'TBPH', 'TC', 'TCBI', 'TCBK', 'TCCO', 'TCDA', 'TCF', 'TCFC', 'TCMD', 'TCOM', 'TCON', 'TCRR', 'TCX', 'TDAC', 'TEAM', 'TECH', 'TEDU', 'TELA', 'TELL', 'TENB', 'TENX', 'TER', 'TESS', 'TFFP', 'TFSL', 'TGA', 'TGLS', 'TGTX', 'TH', 'THBR', 'THCA', 'THCB', 'THFF', 'THMO', 'THRM', 'THRY', 'THTX', 'TIG', 'TIGO', 'TIGR', 'TILE', 'TIPT', 'TITN', 'TLC', 'TLGT', 'TLMD', 'TLND', 'TLRY', 'TLS', 'TLSA', 'TMDI', 'TMDX', 'TMTS', 'TMUS', 'TNAV', 'TNDM', 'TNXP', 'TOMZ', 'TOPS', 'TOTA', 'TOUR', 'TOWN', 'TPCO', 'TPIC', 'TPTX', 'TRCH', 'TREE', 'TRHC', 'TRIB', 'TRIL', 'TRIP', 'TRIT', 'TRMB', 'TRMD', 'TRMK', 'TRMT', 'TRNS', 'TROW', 'TRS', 'TRST', 'TRUE', 'TRUP', 'TRVG', 'TRVI', 'TRVN', 'TSBK', 'TSC', 'TSCO', 'TSEM', 'TSHA', 'TSLA', 'TSRI', 'TTCF', 'TTD', 'TTEC', 'TTEK', 'TTGT', 'TTMI', 'TTNP', 'TTOO', 'TTWO', 'TUSK', 'TVTX', 'TVTY', 'TW', 'TWCT', 'TWIN', 'TWNK', 'TWOU', 'TWST', 'TXG', 'TXMD', 'TXN', 'TXRH', 'TYHT', 'TYME', 'TZAC', 'TZOO', 'UAL', 'UBCP', 'UBFO', 'UBOH', 'UBSI', 'UBX', 'UCBI', 'UCL', 'UCTT', 'UEIC', 'UEPS', 'UFCS', 'UFPI', 'UFPT', 'UG', 'UHAL', 'UIHC', 'UK', 'ULBI', 'ULH', 'ULTA', 'UMBF', 'UMPQ', 'UNAM', 'UNB', 'UNIT', 'UNTY', 'UONE', 'UONEK', 'UPLD', 'UPWK', 'URBN', 'URGN', 'UROV', 'USAK', 'USAP', 'USAT', 'USAU', 'USCR', 'USEG', 'USIO', 'USLM', 'USWS', 'UTHR', 'UTMD', 'UTSI', 'UVSP', 'UXIN', 'VACQ', 'VALU', 'VBFC', 'VBIV', 'VBLT', 'VBTX', 'VC', 'VCEL', 'VCNX', 'VCTR', 'VCYT', 'VECO', 'VEON', 'VERB', 'VERI', 'VERO', 'VERU', 'VERX', 'VERY', 'VFF', 'VG', 'VIAC', 'VIACA', 'VIAV', 'VICR', 'VIE', 'VIH', 'VIOT', 'VIR', 'VIRC', 'VIRT', 'VISL', 'VITL', 'VIVE', 'VIVO', 'VJET', 'VKTX', 'VLDR', 'VLGEA', 'VLY', 'VMAC', 'VMAR', 'VMD', 'VNDA', 'VNET', 'VNOM', 'VOD', 'VOXX', 'VRA', 'VRAY', 'VRCA', 'VREX', 'VRM', 'VRME', 'VRNA', 'VRNS', 'VRNT', 'VRRM', 'VRSK', 'VRSN', 'VRTS', 'VRTU', 'VRTX', 'VSAT', 'VSEC', 'VSPR', 'VSTA', 'VSTM', 'VTGN', 'VTNR', 'VTRS', 'VTRU', 'VTSI', 'VTVT', 'VUZI', 'VVPR', 'VXRT', 'VYGR', 'VYNE', 'WABC', 'WAFD', 'WAFU', 'WASH', 'WATT', 'WB', 'WBA', 'WDAY', 'WDC', 'WDFC', 'WEN', 'WERN', 'WETF', 'WEYS', 'WHLM', 'WHLR', 'WIFI', 'WILC', 'WIMI', 'WINA', 'WING', 'WINT', 'WIRE', 'WISA', 'WIX', 'WKEY', 'WKHS', 'WLDN', 'WLFC', 'WLTW', 'WMG', 'WNEB', 'WORX', 'WPRT', 'WRAP', 'WRLD', 'WSBC', 'WSBF', 'WSC', 'WSFS', 'WSG', 'WSTG', 'WTBA', 'WTER', 'WTFC', 'WTRE', 'WTRH', 'WVE', 'WVFC', 'WVVI', 'WW', 'WWD', 'WWR', 'WYNN', 'XAIR', 'XBIO', 'XBIT', 'XCUR', 'XEL', 'XELA', 'XELB', 'XENE', 'XENT', 'XERS', 'XFOR', 'XGN', 'XLNX', 'XLRN', 'XNCR', 'XNET', 'XOMA', 'XONE', 'XP', 'XPEL', 'XPER', 'XRAY', 'XSPA', 'XTLB', 'YGMZ', 'YI', 'YJ', 'YMAB', 'YNDX', 'YORW', 'YQ', 'YRCW', 'YSAC', 'YTEN', 'YTRA', 'YVR', 'YY', 'Z', 'ZAGG', 'ZBRA', 'ZCMD', 'ZEAL', 'ZEUS', 'ZG', 'ZGNX', 'ZGYH', 'ZI', 'ZION', 'ZIOP', 'ZIXI', 'ZKIN', 'ZLAB', 'ZM', 'ZNGA', 'ZNTL', 'ZS', 'ZSAN', 'ZUMZ', 'ZVO', 'ZYNE', 'ZYXI',],
                     'Others': ['JWN','KSS','HMC','BRK-A','PROG','DS','OBSV']}

ticker_group_dict['Russell 3000'] = sorted(ticker_group_dict['Russell 1000'] + ticker_group_dict['Russell 2000'])

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
                   'ETF': f"Exchange-traded fund (ETF) is a basket of securities that trade on an exchange. Unlike mutual funds (which only trade once a day after the market closes), ETF is just like a stock and share prices fluctuate all day as the ETF is bought and sold.\n\nExchange-traded note (ETN) is a basket of unsecured debt securities that track an underlying index of securities and trade on a major exchange like a stock.\n\nDifference: Investing ETF is investing in a fund that holds the asset it tracks. That asset may be stocks, bonds, gold or other commodities, or futures contracts. In contrast, ETN is more like a bond. It's an unsecured debt note issued by an institution. If the underwriter (usually a bank) were to go bankrupt, the investor would risk a total default.",
                   'Major Market Indices': f"https://www.investing.com/indices/major-indices",
                   'DOW 30': f"Dow Jones Industrial Average 30 Components",
                   'NASDAQ 100': f"A stock market index made up of 103 equity securities issued by 100 of the largest non-financial companies listed on the Nasdaq stock market.\n\nThe complete index, NASDAQ Composite (COMP), has 2,667 securities as of February 2020.\n\nBecause the index is weighted by market capitalization, the index is rather top-heavy. In fact, the top 10 stocks in the Nasdaq Composite account for one-third of the index’s performance.",
                   'S&P 500': f"A stock market index that measures the stock performance of 500 large companies listed on stock exchanges in the United States.\n\nIndex funds that track the S&P 500 have been recommended as investments by Warren Buffett, Burton Malkiel, and John C. Bogle for investors with long time horizons.",
                   'Russell 1000': f"The Russell 1000 Index, a subset of the Russell 3000 Index, represents the 1000 top companies by market capitalization in the United States.\n\nThe Russell 1000 index comprises approximately 92% of the total market capitalization of all listed stocks in the U.S. equity market and is considered a bellwether index for large-cap investing.\n\nNote: Russell 3000 = Russell 1000 (large cap) + Russell 2000 (small cap)",
                   'Russell 2000': f"The Russell 2000 Index, a subset of the Russell 3000 Index, includes ~2,000 smallest-cap American companies in the Russell 3000 Index.",
                   'Russell 3000': f"The Russell 3000 Index, a market-capitalization-weighted equity index maintained by FTSE Russell, provides exposure to the entire U.S. stock market and represents about 98% of all U.S incorporated equity securities.\n\nRussell 3000 = Russell 1000 (larger cap) + Russell 2000 (smaller cap).",
                   'NASDAQ Composite': f"https://en.wikipedia.org/wiki/NASDAQ_Composite",
                   'Others': f"Others"}

def ticker_preprocessing():
    global ticker_group_dict
    global subgroup_group_dict
    global ticker_subgroup_dict

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

ticker_preprocessing()

###########################################################################################

nasdaqlisted_df = pd.DataFrame()
otherlisted_df = pd.DataFrame()
global_data_root_dir = join(str(pathlib.Path.home()), ".investment")

###########################################################################################

# references:
# https://quant.stackexchange.com/questions/1640/where-to-download-list-of-all-common-stocks-traded-on-nyse-nasdaq-and-amex
# http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
def download_nasdaqtrader_data(data_root_dir: str = None):
    if data_root_dir is None:
         raise ValueError("Error: data_root_dir cannot be None")

    data_dir = join(data_root_dir, "ticker_data/nasdaqtrader")
    if not os.path.exists(data_dir):
        try:
            pathlib.Path(data_dir).mkdir(parents=True, exist_ok=True)
        except:
            raise IOError(f"cannot create data dir: {data_dir}")
    ftp_server = 'ftp.nasdaqtrader.com'
    ftp_username = 'anonymous'
    ftp_password = 'anonymous'
    ftp = ftplib.FTP(ftp_server)
    ftp.login(ftp_username, ftp_password)
    files = [('SymbolDirectory/nasdaqlisted.txt', join(data_dir, 'nasdaqlisted.txt')), 
             ('SymbolDirectory/otherlisted.txt',  join(data_dir, 'otherlisted.txt' ))]
    for file_ in files:
        with open(file_[1], "wb") as f:
            ftp.retrbinary("RETR " + file_[0], f.write)
    ftp.quit()


def load_nasdaqtrader_data(data_root_dir: str = None):

    from ._data import timedata

    if data_root_dir is None:
        raise ValueError("Error: data_root_dir cannot be None")

    file1 = pathlib.Path(join(data_root_dir, "ticker_data/nasdaqtrader/nasdaqlisted.txt"))
    file2 = pathlib.Path(join(data_root_dir, "ticker_data/nasdaqtrader/otherlisted.txt"))

    to_download = False

    if file1.exists():
        if timedata().now.datetime - timedata(time_stamp=file1.stat().st_ctime).datetime > timedelta(days=7): # creation time
            to_download = True
    else:
        to_download = True

    if file2.exists():
        if timedata().now.datetime - timedata(time_stamp=file2.stat().st_ctime).datetime > timedelta(days=7): # creation time
            to_download = True
    else:
        to_download = True

    if to_download:
        download_nasdaqtrader_data(data_root_dir = data_root_dir) # always get the most up-to-date version

    global nasdaqlisted_df
    global otherlisted_df

    nasdaqlisted_df = pd.read_csv(file1,sep='|',header=0,skipfooter=1,engine='python')
    otherlisted_df = pd.read_csv(file2,sep='|',header=0,skipfooter=1,engine='python')
    nasdaqlisted_df['ticker'] = nasdaqlisted_df['Symbol'].str.replace('\.','\-')
    otherlisted_df['ticker'] = otherlisted_df['NASDAQ Symbol'].str.replace('\.','\-')
    nasdaqlisted_df = nasdaqlisted_df[ (nasdaqlisted_df['Test Issue'] == 'N') & (nasdaqlisted_df['NextShares'] == 'N') ].drop(['Test Issue','Symbol','NextShares','Round Lot Size'], axis=1)
    otherlisted_df = otherlisted_df[ otherlisted_df['Test Issue'] == 'N' ].drop(['Test Issue','NASDAQ Symbol','ACT Symbol','CQS Symbol','Round Lot Size'], axis=1)


load_nasdaqtrader_data(data_root_dir=global_data_root_dir)
   
###########################################################################################

class Ticker(object):
    def __init__(self, ticker=None, ticker_data_dict=None):
        if ticker is None:
            if ticker_data_dict is None:
                raise ValueError('error')
            else:
                self.ticker_data_dict = ticker_data_dict
                self.ticker = ticker_data_dict['ticker']
        else:
            if ticker_data_dict is None:
                from ._data import get_ticker_data_dict
                self.ticker = ticker
                self.ticker_data_dict = get_ticker_data_dict(ticker=self.ticker)
            else:
                self.ticker_data_dict = ticker_data_dict
                self.ticker = ticker_data_dict['ticker']

    @property
    def nasdaq_listed(self):
        df = nasdaqlisted_df[ nasdaqlisted_df['ticker'] == self.ticker ]
        n_len = len(df)
        if n_len == 0:
            return False
        elif n_len == 1:
            return True
        else:
            raise ValueError(f'self.ticker = {self.ticker}, n_len should not be >1')

    @property
    def nasdaq_security_name(self):
        if self.nasdaq_listed:
            sn = nasdaqlisted_df[ nasdaqlisted_df['ticker'] == self.ticker ]['Security Name'].iloc[0]
            return sn
        else:
            raise ValueError("this question should be asked for NASDAQ-listed ticker only")

    @property
    def nasdaq_market_category(self):
        if self.nasdaq_listed:
            mc = nasdaqlisted_df[ nasdaqlisted_df['ticker'] == self.ticker ]['Market Category'].iloc[0]
            mc_dict = {'Q': 'NASDAQ Global Select MarketSM', 'G': 'NASDAQ Global MarketSM', 'S': 'NASDAQ Capital Market'}
            return mc_dict[mc]
        else:
            raise ValueError("this question should be asked for NASDAQ-listed ticker only")

    @property
    def nasdaq_financial_status(self):
        if self.nasdaq_listed:
            fs = nasdaqlisted_df[ nasdaqlisted_df['ticker'] == self.ticker ]['Financial Status'].iloc[0]
            fs_dict = {'D': 'Deficient: Issuer Failed to Meet NASDAQ Continued Listing Requirements',
                       'E': 'Delinquent: Issuer Missed Regulatory Filing Deadline',
                       'Q': 'Bankrupt: Issuer Has Filed for Bankruptcy',
                       'N': 'Normal', # NOT Deficient, Delinquent, or Bankrupt.',
                       'G': 'Deficient and Bankrupt',
                       'H': 'Deficient and Delinquent',
                       'J': 'Delinquent and Bankrupt',
                       'K': 'Deficient, Delinquent, and Bankrupt',}
            return fs_dict[fs]
        else:
            raise ValueError("this question should be asked for NASDAQ-listed ticker only")

    @property
    def nasdaq_etf(self):
        if self.nasdaq_listed:
            etf = nasdaqlisted_df[ nasdaqlisted_df['ticker'] == self.ticker ]['ETF'].iloc[0]
            if etf == 'Y':
                return True
            elif etf == 'N':
                return False
            else:
                raise ValueError('unexpected ETF answer')
        else:
            raise ValueError("this question should be asked for NASDAQ-listed ticker only")

    @property
    def non_nasdaq_listed(self):
        df = otherlisted_df[ otherlisted_df['ticker'] == self.ticker ]
        n_len = len(df)
        if n_len == 0:
            return False
        elif n_len == 1:
            return True
        else:
            raise ValueError(f'self.ticker = {self.ticker}, n_len should not be >1')

    @property
    def non_nasdaq_security_name(self):
        if self.non_nasdaq_listed:
            sn = otherlisted_df[ otherlisted_df['ticker'] == self.ticker ]['Security Name'].iloc[0]
            return sn
        else:
            raise ValueError("this question should be asked for non-NASDAQ-listed ticker only")

    @property
    def non_nasdaq_exchange(self):
        if self.non_nasdaq_listed:
            ex = otherlisted_df[ otherlisted_df['ticker'] == self.ticker ]['Exchange'].iloc[0]
            ex_dict = {'A': 'NYSE MKT',
                       'N': 'New York Stock Exchange (NYSE)',
                       'P': 'NYSE ARCA',
                       'Z': 'BATS Global Markets (BATS)',
                       'V': 'Investors\' Exchange, LLC (IEXG)'}
            return ex_dict[ex]
        else:
            raise ValueError("this question should be asked for non-NASDAQ-listed ticker only")

    @property
    def non_nasdaq_etf(self):
        if self.non_nasdaq_listed:
            etf = otherlisted_df[ otherlisted_df['ticker'] == self.ticker ]['ETF'].iloc[0]
            if etf == 'Y':
                return True
            elif etf == 'N':
                return False
            else:
                raise ValueError('unexpected ETF answer')
        else:
            raise ValueError("this question should be asked for non-NASDAQ-listed ticker only")

    @property
    def in_dow30(self):
        if self.ticker in ticker_group_dict['DOW 30']:
            return True
        else:
            return False

    @property
    def in_nasdaq100(self):
        if self.ticker in ticker_group_dict['NASDAQ 100']:
            return True
        else:
            return False

    @property
    def in_sandp500(self):
        if self.ticker in ticker_group_dict['S&P 500']:
            return True
        else:
            return False

    @property
    def in_russell1000(self):
        if self.ticker in ticker_group_dict['Russell 1000']:
            return True
        else:
            return False

    @property
    def in_russell2000(self):
        if self.ticker in ticker_group_dict['Russell 2000']:
            return True
        else:
            return False

    @property
    def in_russell3000(self):
        if self.ticker in ticker_group_dict['Russell 3000']:
            return True
        else:
            return False

    @property
    def in_nasdaq_composite(self):
        if self.ticker in ticker_group_dict['NASDAQ Composite']:
            return True
        else:
            return False       

    @property
    def longName(self):
        return self.ticker_info['longName']

    @property
    def longBusinessSummary(self):
        return self.ticker_info['longBusinessSummary']

    @property
    def logo(self):
        return self.ticker_info['logo']

    @property
    def ticker_info(self):
        return self.ticker_data_dict['info']

    @property
    def ticker_history(self):
        return self.ticker_data_dict['history']

    @property
    def last_date(self):
        return self.ticker_history['Date'].iloc[-1]

    @property
    def last_close_price(self):
        return self.ticker_history['Close'].iloc[-1]

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

    def key_value(self, this_key):
        if this_key is not None:
            if self.ticker_info is not None:
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
    def price_target_upside_pct(self):
        if self.price_target is None:
            return None
        else:
            return 100 * (self.price_target - self.last_close_price) / self.last_close_price

    @property
    def prob_price_target_upside(self):
        if self.price_target_upside_pct is not None: 
            return sigmoid(self.price_target_upside_pct/100)
        return None

    @property
    def last_1yr_dividends_pct(self):
        if self.pay_dividends:
            dividends_df = self.ticker_data_dict['dividends'].reset_index(level=0)
            dividends_df['Date'] = pd.to_datetime(dividends_df['Date'], format='%Y-%m-%d', utc=True)
            last_1yr_dividends_df = dividends_df[ dividends_df['Date'] > (datetime.now(tz=timezone.utc) - timedelta(days=365.25)) ]
            date_close_df = self.ticker_data_dict['history'][['Date','Close']]
            dividends_info_df = pd.DataFrame(columns=['date','dividends','yield_pct'])
            for idx, row in last_1yr_dividends_df.iterrows():
                try:
                    close_price_on_this_date = float(date_close_df[date_close_df.Date == row['Date']].Close)
                    dividends_yield_percent = 100*row['Dividends']/close_price_on_this_date
                except:
                    dividends_yield_percent = 0
                dividends_info_df = dividends_info_df.append({'date': row['Date'].date(), 'dividends': row['Dividends'], 'yield_pct': dividends_yield_percent}, ignore_index = True)
            #print(dividends_info_df)
            if len(dividends_info_df) > 0:
                return dividends_info_df['yield_pct'].sum()
        return 0

    @property
    def pay_dividends(self):
        if 'dividends' in self.ticker_data_dict.keys():
            dividends_df = self.ticker_data_dict['dividends'].reset_index(level=0)
            if len(dividends_df) > 0:
                return True
        return False

    @property
    def EV_to_EBITDA(self):
        """
        Enterprise value / EBITDA (earnings before interest, taxes, depreciation, and amortization.)
        The lower the better
        """
        return self.key_value('enterpriseToEbitda')

    @property
    def forwardPE(self):
        """
        Price-to-earnings ratio = Current market price per share / forwardEps
        """
        return self.key_value('forwardPE')

    @property
    def trailingPE(self):
        """
        Price-to-earnings ratio = Current market price per share / trailingEps
        """
        return self.key_value('trailingPE')

    @property
    def PEG_ratio(self):
        """
        forward PE / EPS growth (5 year)
        """
        return self.key_value('pegRatio')

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
        return self.key_value('forwardEps')

    @property
    def trailingEps(self):
        return self.key_value('trailingEps')

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