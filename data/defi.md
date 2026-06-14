# DeFi and AMMs

Decentralized finance (DeFi) recreates financial services such as trading, lending, and
borrowing using smart contracts instead of intermediaries. A core primitive is the automated
market maker (AMM), a type of decentralized exchange that prices assets with a mathematical
formula rather than a traditional order book.

The most common AMM design uses a constant-product formula, x * y = k, where x and y are the
reserves of two tokens in a liquidity pool and k is held constant. Liquidity providers deposit
both tokens and earn a share of trading fees, but they are exposed to impermanent loss when the
relative price of the two assets diverges. Lending protocols let users supply collateral to
borrow assets, with positions liquidated if collateral value falls below a required threshold.
Major DeFi risks include smart-contract exploits, oracle manipulation, and cascading
liquidations during sharp market moves.
