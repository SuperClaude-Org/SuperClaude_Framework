# Chrome DevTools MCP Server

**Purpose**: Performance analysis, debugging, and real-time browser inspection

## Triggers
- Performance auditing and analysis requests
- Debugging of layout issues (e.g., CLS)
- Investigation of slow loading times (e.g., LCP)
- Analysis of console errors and network requests
- Real-time inspection of the DOM and CSS

## Choose When
- **For deep performance analysis**: When you need to understand performance bottlenecks.
- **For live debugging**: To inspect the runtime state of a web page and debug live issues.
- **For network analysis**: To inspect network requests and identify issues like CORS errors.
- **Not for E2E testing**: Use Playwright for end-to-end testing scenarios.
- **Not for static analysis**: Use native Claude for code review and logic validation.

## Works Best With
- **Sequential**: Sequential plans a performance improvement strategy → Chrome DevTools analyzes and verifies the improvements.
- **Playwright**: Playwright automates a user flow → Chrome DevTools analyzes the performance of that flow.

## Examples
```
"analyze the performance of this page" → Chrome DevTools (performance analysis)
"why is this page loading slowly?" → Chrome DevTools (performance analysis)
"debug the layout shift on this element" → Chrome DevTools (live debugging)
"check for console errors on the homepage" → Chrome DevTools (live debugging)
"what network requests are failing?" → Chrome DevTools (network analysis)
"test the login flow" → Playwright (browser automation)
"review this function's logic" → Native Claude (static analysis)
```