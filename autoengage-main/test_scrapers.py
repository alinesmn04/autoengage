import traceback

try:
    from platform_facebook import facebook_search_posts
    print("Testing Facebook:")
    print(facebook_search_posts.invoke({'query': 'marketing', 'results_max': 5}))
except Exception as e:
    traceback.print_exc()

try:
    from platform_linkedin import linkedin_search_posts
    print("\nTesting LinkedIn:")
    print(linkedin_search_posts.invoke({'query': 'marketing', 'results_max': 5}))
except Exception as e:
    traceback.print_exc()
