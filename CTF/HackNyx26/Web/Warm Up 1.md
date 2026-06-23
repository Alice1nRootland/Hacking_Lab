<img width="565" height="677" alt="image" src="https://github.com/user-attachments/assets/d1f06431-21f3-4110-b7d0-1a6bba951aee" />

The challenge presents a mock e-commerce store called "Defcon Gear" featuring three accessible pages: `Home`, `About`, and `Products`. The goal is to locate a leaked flag hidden within the application's backend architecture.

<img width="1750" height="515" alt="image" src="https://github.com/user-attachments/assets/87dbc41a-5289-4dd6-91be-1664bc8dff99" />

<img width="1780" height="427" alt="image" src="https://github.com/user-attachments/assets/4e572875-0b7b-4a3f-9ae7-108547500946" />

<img width="1490" height="845" alt="image" src="https://github.com/user-attachments/assets/08bdc83b-ab12-4533-a522-b97edc33108e" />

#### Reconnaissance & Source Analysis

Inspection of the front-end HTML revealed a standard `GET` search form on `products.php`:

<img width="780" height="127" alt="image" src="https://github.com/user-attachments/assets/adf9ac12-b45c-4be7-81f6-4dd4ab92336b" />

A quick check of the linked `style.css` stylesheet revealed several CSS classes that were **not** rendered anywhere in the DOM:

- `.login-container`
- `.error-box`
- `.response-area`

The existence of an un-rendered `.error-box` strongly suggested that the back-end had custom error-handling logic designed to catch and visually display database failures to the user.

#### The Exploit

To test if the search parameter was passing unsanitized input to the database, a single quotation mark (`'`) was submitted to break the string literal of the backend query:

**Payload:** `?search='`

#### The Result

The application instantly broke, returning an uncaught MariaDB syntax error, a partial stack trace, and **the flag printed directly to the DOM**:

<img width="1461" height="522" alt="image" src="https://github.com/user-attachments/assets/381c844d-c0f8-44db-b46d-37686681ccb7" />

**Flag: *HNYX{MySqL_3rR0r_4nYwh3R3???!!}***
