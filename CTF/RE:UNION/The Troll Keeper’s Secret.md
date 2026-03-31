<img width="496" height="570" alt="image" src="https://github.com/user-attachments/assets/b533a3d4-5c82-467b-9ee8-5aabc8f7410b" />

i right away run this command 

`grep -n "SLEEP" The\ Troll\ Keeper’s\ Secret.txt`

<img width="1594" height="623" alt="image" src="https://github.com/user-attachments/assets/fa76e869-09b3-41be-b403-66d9efb64a9d" />

then you can see the pattern 

## **Step 1: Identify the Vulnerability**

By inspecting the logs (`The Troll Keeper’s Secret.txt`), multiple queries contain the `SLEEP()` function:

```
SELECT idFROM sessionsWHERE id='1'AND IF(SUBSTRING((SELECT @@datadir),1,1)='/', SLEEP(5),0);
```

**Observation:**

- The application executes a query with user-controllable input.
- When the condition is **true**, the query sleeps (`SLEEP(5)`), causing a noticeable delay in response.
- This is a **time-based blind SQL injection**, ideal for extracting data character by character.

---

## **Step 2: Understand the Exploit**

- SQL function `SUBSTRING((SELECT @@datadir), n, 1)` extracts the **nth character** of the `datadir` variable.
- `IF(condition, SLEEP(5), 0)` pauses execution if the guessed character is correct.
- By iterating over positions and guessing characters, we can reconstruct the full path.

---

## **Step 3: Extract Characters**

From the logs, we collected each character with a delayed response:

| **Timestamp** | **Index Position** | **Guessed Char** | **Response Time** | **Status** |
| --- | --- | --- | --- | --- |
| 21:00:03 | 1 | **/** | 5.04s | **HIT** |
| 21:00:41 | 2 | **v** | 5.12s | **HIT** |
| 21:00:43 | 3 | **a** | 5.07s | **HIT** |
| 21:00:46 | 4 | **r** | 5.12s | **HIT** |
| 21:00:50 | 5 | **/** | 5.18s | **HIT** |
| ... | ... | ... | ... | ... |

**The Sequence:**

1. `21:00:03` -> `/`
2. `21:00:41` -> `v`
3. `21:00:43` -> `a`
4. `21:00:46` -> `r`
5. `21:00:50` -> `/`
6. `21:00:52` -> `w`
7. `21:01:09` -> `w`
8. `21:01:13` -> `w`
9. `21:01:19` -> `/`
10. `21:01:26` -> `a`
11. `21:01:55` -> `d`
12. `21:02:32` -> `m`
13. `21:02:35` -> `i`
14. `21:02:54` -> `n`
15. `21:02:57` -> `/`
16. `21:03:02` -> `c`
17. `21:03:04` -> `o`
18. `21:03:13` -> `n`
19. `21:03:16` -> `s`
20. `21:03:20` -> `o`
21. `21:03:32` -> `l`
22. `21:03:40` -> `e`
23. `21:03:45` -> `/`
24. `21:03:53` -> `s`
25. `21:04:00` -> `e`
26. `21:04:03` -> `c`
27. `21:04:06` -> `r`
28. `21:04:08` -> `e`
29. `21:04:36` -> `t`
30. `21:04:47` -> `/`
31. `21:04:50` -> `T`
32. `21:05:02` -> `r`
33. `21:05:34` -> `o`
34. `21:05:36` -> `l`
35. `21:05:44` -> `l`
36. `21:05:47` -> `K`
37. `21:05:55` -> `e`
38. `21:06:03` -> `e`
39. `21:06:20` -> `p`
40. `21:06:34` -> `e`
41. `21:06:55` -> `r`
42. `21:07:28` -> `T`
43. `21:07:31` -> `r`
44. `21:07:33` -> `e`
45. `21:07:46` -> `a`
46. `21:07:54` -> `s`
47. `21:07:57` -> `u`
48. `21:08:02` -> `r`
49. `21:08:23` -> `e`
50. `21:08:35` -> `M`
51. `21:08:40` -> `a`
52. `21:08:53` -> `p`
53. `21:09:07` -> `.`
54. `21:09:12` -> `t`
55. `21:09:16` -> `x`
56. `21:09:21` -> `t`

---

## **Step 4: Reconstruct the Full Path**

Concatenating all characters in order, the MySQL `datadir` path is:

```
/var/www/admin/console/secret/TrollKeeperTreasureMap.txt
```

**Screenshot suggestion:**

- Show the final concatenated path in a table or as plain text.

---

## **Step 5: Flag Format**

Most CTFs require a format-friendly flag. In this challenge, the likely flag is:

```
RE:CTF{var_www_admin_console_secret_TrollKeeperTreasureMap_txt}```
