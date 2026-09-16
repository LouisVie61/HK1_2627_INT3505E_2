- rest - phong cach thiet ke api, con json chi don gian la mot kieu presentation 
- post = create, put = update fully, patch = update partially
- RESTful API có cache thì không cần Authorization
    - RESTful API có cache thì không cần Authorization: theo chuan kien thuc sample = wrong
    - in reality if cache is using for security caching token --> it's true; and the content need: return send Authorization + cache(token)
    - it's definitely wrong if we don't have cache and don't send authorization as a header in the request 

- SAI ban chat: thieu mot constraint cua rest --> Non rest-api
    - chu y: HTTP-based-RPC