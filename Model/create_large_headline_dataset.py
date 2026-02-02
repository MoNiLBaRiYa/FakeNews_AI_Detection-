"""
Create a LARGE headline dataset by extracting from existing articles
and adding more real/fake headlines
"""
import pandas as pd
import random
import os
import re

def extract_headlines_from_articles():
    """Extract multiple headline-like sentences from each article"""
    print("📰 Extracting headlines from article dataset...")
    
    # Load existing article datasets
    fake_path = os.path.join(os.path.dirname(__file__), 'Fake.csv')
    true_path = os.path.join(os.path.dirname(__file__), 'True.csv')
    
    real_headlines = []
    fake_headlines = []
    
    # Extract from True.csv
    if os.path.exists(true_path):
        df_true = pd.read_csv(true_path)
        print(f"✅ Loaded {len(df_true)} real articles")
        
        for text in df_true['text']:
            if isinstance(text, str) and len(text) > 100:
                # Split into sentences
                sentences = re.split(r'[.!?]+', text)
                
                # Take first 3 sentences as potential headlines
                for sentence in sentences[:3]:
                    sentence = sentence.strip()
                    # Filter for headline-like sentences (20-200 chars)
                    if 20 < len(sentence) < 200:
                        # Remove common article prefixes
                        sentence = re.sub(r'^(WASHINGTON|NEW YORK|LONDON|REUTERS|AP)\s*[-:]\s*', '', sentence, flags=re.IGNORECASE)
                        sentence = re.sub(r'^\([^)]+\)\s*[-:]\s*', '', sentence)
                        sentence = sentence.strip()
                        
                        if len(sentence) > 20:
                            real_headlines.append(sentence)
        
        print(f"✅ Extracted {len(real_headlines)} real headlines")
    
    # Extract from Fake.csv
    if os.path.exists(fake_path):
        df_fake = pd.read_csv(fake_path)
        print(f"✅ Loaded {len(df_fake)} fake articles")
        
        for text in df_fake['text']:
            if isinstance(text, str) and len(text) > 100:
                # Split into sentences
                sentences = re.split(r'[.!?]+', text)
                
                # Take first 3 sentences
                for sentence in sentences[:3]:
                    sentence = sentence.strip()
                    if 20 < len(sentence) < 200:
                        fake_headlines.append(sentence)
        
        print(f"✅ Extracted {len(fake_headlines)} fake headlines")
    
    return real_headlines, fake_headlines

def add_business_tech_headlines():
    """Add more business and tech headlines (common in news) - UPDATED 2026"""
    business_headlines = [
        # Modern Indian Startups & IPOs
        "PhonePe raises $850 million in funding round at $12 billion valuation",
        "Zepto expands quick commerce operations to 15 new cities",
        "Oyo reports 40% revenue growth in Q3 2025",
        "Swiggy Instamart competes with Zepto in 10-minute delivery",
        "Paytm stock rises 8% on strong quarterly results",
        "Byju's restructures debt amid financial challenges",
        "Zomato acquires quick commerce startup for $200 million",
        "Flipkart prepares for IPO targeting $60 billion valuation",
        "Ola Electric reports record EV sales in December",
        "Meesho crosses 150 million monthly active users",
        "CRED launches new credit card payment feature",
        "Dream11 expands into international markets",
        "Razorpay becomes India's most valuable fintech startup",
        "Nykaa stock gains 12% on beauty segment growth",
        "PolicyBazaar reports profitability in insurance business",
        "Lenskart raises funds at $5 billion valuation",
        "Urban Company expands services to 50 cities",
        "Dunzo faces funding crunch amid market slowdown",
        "ShareChat lays off 20% workforce in restructuring",
        "Unacademy pivots to test preparation segment",
        
        # Traditional Business News
        "Company reports strong quarterly earnings with 15% revenue growth",
        "Tech startup raises $50 million in Series B funding round",
        "Stock market closes higher on positive economic data",
        "Central bank announces interest rate decision",
        "Merger deal valued at $2 billion receives regulatory approval",
        "Retail sales increase 3.5% in latest quarter",
        "Manufacturing sector shows signs of recovery",
        "Unemployment rate drops to lowest level in 5 years",
        "New trade agreement signed between major economies",
        "Consumer confidence index reaches 10-year high",
        "Housing market shows steady growth in major cities",
        "Inflation rate eases to 4.2% from previous 5.1%",
        "Technology sector leads market gains for third consecutive month",
        "Automotive industry announces shift to electric vehicles",
        "Pharmaceutical company receives FDA approval for new drug",
        "E-commerce sales surge during holiday shopping season",
        "Banking sector reports improved loan growth",
        "Energy prices stabilize after recent volatility",
        "Startup ecosystem attracts record venture capital investment",
        "Corporate earnings exceed analyst expectations",
        
        # IPO & Market News
        "New-age companies target Rs 50,000 crore in IPO fundraising",
        "Tech unicorns plan public listings in 2026",
        "IPO market shows strong momentum with 15 listings planned",
        "Investors show appetite for technology sector IPOs",
        "Market conditions favorable for startup public offerings",
        "Profitability becomes key factor for IPO success",
        "Public investors become more selective in tech investments",
        "Valuation expectations moderate for new-age companies",
        "IPO pipeline includes fintech and e-commerce leaders",
        "Regulatory approvals received for major public offerings",
        
        # More Modern Headlines
        "Supply chain disruptions begin to ease",
        "Digital payment adoption reaches new milestone",
        "Renewable energy capacity increases significantly",
        "Real estate investment trusts show strong performance",
        "Cryptocurrency market experiences high volatility",
        "Food delivery platforms report user growth",
        "Telecom operators announce 5G network expansion",
        "Airline industry shows recovery in passenger numbers",
        "Retail chains expand store footprint in tier-2 cities",
        "Insurance sector reports premium growth",
        "Logistics companies invest in automation technology",
        "Healthcare sector attracts private equity investment",
        "Education technology platforms see increased adoption",
        "Fintech companies partner with traditional banks",
        "Cloud computing services revenue grows substantially",
        "Semiconductor shortage impacts electronics production",
        "Streaming services compete for subscriber growth",
        "Social media platforms update privacy policies",
        "Cybersecurity spending increases across industries",
        "Artificial intelligence adoption accelerates in enterprises",
        "Electric vehicle sales double year-over-year",
        "Green bonds issuance reaches record levels",
        "Gig economy workforce continues to expand",
        "Remote work trends reshape commercial real estate",
        "Subscription-based business models gain popularity",
        "Direct-to-consumer brands challenge traditional retail",
        "Blockchain technology finds new use cases",
        "Quantum computing research makes breakthrough",
        "Biotechnology sector attracts significant funding",
        "Space exploration companies announce new missions",
    ]
    return business_headlines

def create_large_dataset():
    """Create comprehensive headline dataset"""
    print("=" * 70)
    print("📊 CREATING LARGE HEADLINE DATASET")
    print("=" * 70)
    
    # Extract from existing articles
    real_from_articles, fake_from_articles = extract_headlines_from_articles()
    
    # Add business/tech headlines
    business_headlines = add_business_tech_headlines()
    
    # Combine real headlines
    all_real = real_from_articles + business_headlines
    
    # Remove duplicates
    all_real = list(set(all_real))
    random.shuffle(all_real)
    
    print(f"\n📊 Available Headlines:")
    print(f"   Real (from articles): {len(real_from_articles)}")
    print(f"   Real (business/tech): {len(business_headlines)}")
    print(f"   Real (total unique): {len(all_real)}")
    print(f"   Fake (from articles): {len(set(fake_from_articles))}")
    
    # Use ALL available headlines (no limit)
    real_headlines = all_real
    
    # Take same number of fake headlines to balance dataset
    fake_headlines = list(set(fake_from_articles))
    random.shuffle(fake_headlines)
    
    # Balance the dataset
    min_count = min(len(real_headlines), len(fake_headlines))
    real_headlines = real_headlines[:min_count]
    fake_headlines = fake_headlines[:min_count]
    
    print(f"\n📊 Final Dataset Statistics:")
    print(f"   Real headlines: {len(real_headlines)}")
    print(f"   Fake headlines: {len(fake_headlines)}")
    print(f"   Total: {len(real_headlines) + len(fake_headlines)}")
    
    # Create DataFrame
    df_real = pd.DataFrame({
        'text': real_headlines,
        'label': 1  # 1 = Real
    })
    
    df_fake = pd.DataFrame({
        'text': fake_headlines,
        'label': 0  # 0 = Fake
    })
    
    # Combine and shuffle
    df = pd.concat([df_real, df_fake], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save to CSV
    output_path = os.path.join(os.path.dirname(__file__), 'Headlines_Large.csv')
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Dataset saved to: {output_path}")
    print(f"📈 Ready for training!")
    
    # Show samples
    print("\n📋 Sample Headlines:")
    print("\n🟢 REAL:")
    for headline in real_headlines[:5]:
        print(f"   • {headline[:100]}...")
    print("\n🔴 FAKE:")
    for headline in fake_headlines[:5]:
        print(f"   • {headline[:100]}...")
    
    return output_path

if __name__ == "__main__":
    create_large_dataset()
