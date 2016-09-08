# Betadog
The dog that follows the alpha.

A stock market strategy can typically be trend following since many people do not have enough funds to set the market trend. This can be done in two general ways, by using pre-existing data and back testings or by gathering fresh data and looking out for trend patterns in existing market players. In the market that this code is being tested, the market broker positions are declared. This makes a market following strategy even more plausible.

This project has three parts:gathering of market data, analysis, and finally testing in the market.

Market data can either come from published data, market data API's, or webscraping. This project uses webscraping as a data gathering method since published data can be costly for small players and neophite traders. Webscraping can go lightweight or heavy depending on the source of the data. The lightweight approach uses the network stream to feed the required traffic to
the server datasource. However, a data source that is heavy on javascripting (especially for sites that depend on javascript for interface and content generation) will require an approach that has either a javascript engine or control a browser with a functional javascript engine.
