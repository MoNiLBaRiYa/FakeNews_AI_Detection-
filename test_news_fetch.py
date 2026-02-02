from Backend.FND import fetch_and_predict_news

result = fetch_and_predict_news('technology')

print(f"Total news fetched: {len(result['news'])}")
print(f"\nPredictions breakdown:")
print(f"Real News: {result['predictions'].count('Real News')}")
print(f"Fake News: {result['predictions'].count('Fake News')}")

print(f"\nFirst 5 news items:")
for i in range(min(5, len(result['news']))):
    news = result['news'][i][:150]
    pred = result['predictions'][i]
    print(f"\n{i+1}. [{pred}] {news}...")
