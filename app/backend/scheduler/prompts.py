DAILY_PROMPT= '''
# Daily Dividend Newsletter Prompt

**OBJECTIVE:** Create a concise, mobile-friendly daily market newsletter for finance-aware (but not expert-level) readers.

## FORMAT TEMPLATE:
```
Daily Dividend | {Day}, {Month} {Date}
S&P 500: {S&P_change} | EUROSTOXX 600: {Eurostoxx_change} | FTSE100: {FTSE_change} *no charts needed

🌍 **GLOBAL MACRO HEADLINE 1**
Brief description (max 2 lines)
Market impact: How this affects US/EU/UK/Asia

🏦 **GLOBAL MACRO HEADLINE 2** 
Brief description (max 2 lines)
Market impact: Regional effects

📊 **GLOBAL MACRO HEADLINE 3**
Brief description (max 2 lines)
Market impact: Cross-market implications

🔍 **STOCK SPOTLIGHT**
Company name ±X.X% - Reason for move
Brief context (earnings/news/deal)

💡 **TAKEAWAY**
1-2 sentences: What this means for global markets going forward
Tone: Clear, balanced, slightly cautious

📘 **TERM OF THE DAY**
Financial Term = One-line definition with market relevance
```

## CONTENT REQUIREMENTS:

### Macro Headlines (3 required):
- **Recency:** Prioritize last 24 hours, max 48 hours old
- **Topics:** Central banks, inflation data, trade policy, oil/commodities, key economic releases, major index moves, elections, geopolitical events
- **Geographic scope:** Global perspective with US/EU/UK/Asia impact analysis
- **Length:** 2 lines description + 1 line market impact

### Stock Stories (1-2 required):
- **Focus:** Large-cap NASDAQ, Big Tech, major UK/EU stocks
- **Exception:** Mid/small-cap if major industry-breaking news
- **Triggers:** Earnings beats/misses, M&A, product launches, regulatory news
- **Must include:** Percentage move when available
- **Context:** Brief explanation of why the stock moved

### Market Data:
- **Indices:** S&P 500, EUROSTOXX 600, FTSE 100 (daily % change)
- **No charts needed**
- **Source verification:** Only use verified financial news sources

### Writing Style:
- **Tone:** Professional but accessible, balanced with slight caution
- **Format:** Bold headers, bullet-like spacing, short punchy sentences
- **Mobile-optimized:** Easy to scan on phone screens
- **Emojis:** Use sparingly for visual breaks (🌍🏦📊🔍💡📘)

### Quality Controls:
- **Sources:** Only verified financial news outlets (Reuters, Bloomberg, FT, WSJ, CNBC, MarketWatch)
- **Fact-check:** Cross-reference major claims
- **Relevance:** Every item must have clear market impact
- **Balance:** Mix of positive/negative/neutral news when possible

## EXAMPLE OUTPUT:
```
Daily Dividend | Wed, July 30
S&P 500: +0.3% | EUROSTOXX 600: +0.1% | FTSE 100: +0.5%

🌍 **Fed signals September cut likely**
Powell hints at rate reduction if inflation continues cooling trajectory.
Market impact: Tech stocks rally, dollar weakens vs euro and yen.

🏦 **China manufacturing PMI beats at 50.3**
Factory activity expands for first time in three months on stimulus hopes.
Market impact: Asian markets up 1.2%, commodities gain on demand outlook.

📊 **UK inflation holds at 2.2%**
Core CPI steady, giving BoE room for gradual easing approach.
Market impact: GBP stable, FTSE financials mixed on rate cut timeline.

🔍 **Microsoft +4.1% on AI cloud surge**
Azure revenue up 29% as enterprise AI adoption accelerates.
Competitors Google and Amazon also gain on sector optimism.

💡 **TAKEAWAY**
Central banks globally shifting dovish while growth shows resilience. Markets pricing in soft landing but remain sensitive to data surprises.

📘 **TERM OF THE DAY**
Dovish Pivot = When central banks shift from raising to potentially cutting interest rates
```

## FINAL CHECKLIST:
- [ ] All market data current and accurate
- [ ] 3 macro headlines with clear impact
- [ ] 1-2 stock stories with % moves
- [ ] Balanced tone with slight caution
- [ ] Mobile-friendly formatting
- [ ] Sources verified
- [ ] Under 250 words total
'''
