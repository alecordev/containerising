# Selenium

## Simple usage

1. `docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-firefox:4.1.2-20220131`
2. Point your WebDriver tests to `http://localhost:4444` *
3. To see what is happening inside the container, head to `http://localhost:7900` (password is secret)

## Notes

- `localhost:4444` to access Selenium grid if using docker-compose.
- `docker run -d -p 4444:4444 --shm-size="2g" selenium/standalone-firefox:4.1.1-20220121`

```
from selenium import webdriver
driver = webdriver.Remote(command_executor='http://localhost:4444')
```

## Resources

- https://github.com/SeleniumHQ/docker-selenium
