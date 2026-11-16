# OpenGovData1.0 — public URA carpark tariff data

Separate PUBLIC, data-only repository. No Android source, device information, URA API key, token or other credentials.

This GitHub Actions workflow retrieves URA Car_Park_Details using a *server-side* standard GitHub-hosted runner at 08:20 Singapore time on the 1st of every month (UTC cron 20 0 1 * *). It publishes only the sanitised, dated file ura-carpark-rates.json. A failed sync does not replace the previous file.

The URA_ACCESS_KEY must be stored as a GitHub Actions repository secret. Do not commit the key to this public repository. Grant the workflow Contents: read and write permission.

Source: URA Car Park Details API, https://eservice.ura.gov.sg/maps/api/ . Contains information from the Urban Redevelopment Authority (URA), dated updated_utc in the output file, made available under the Singapore Open Data Licence: https://www.ura.gov.sg/eservices-info/maps/acceptance-grant-licence/ . This project is independent and not government-endorsed. Rates are indicative, not guaranteed real-time prices.

GitHub public standard hosted runner costs are free under the GitHub Actions billing terms. GitHub Actions is a cloud server-side runner; URA can clarify whether its email wording "from your server" accepts this arrangement.

The APK fetches this public JSON without GitHub credentials at https://raw.githubusercontent.com/FaayizFirros/opengovdata-parking-rates/main/ura-carpark-rates.json . It displays tariffs only for bookmarked carparks or those found within 2 km, not generic search results.
