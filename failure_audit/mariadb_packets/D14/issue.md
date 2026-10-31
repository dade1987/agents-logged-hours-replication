# Incorrect result of JSON_TABLE with BIT

Hi,

I found that JSON_TABLE can return incorrect results with the BIT type. This is an example:

{code:sql}
SELECT ord, i, b+0, HEX(b) 
FROM JSON_TABLE(
       '[0,1]',
       '$[*]' COLUMNS (
         ord FOR ORDINALITY,
         i INT PATH '$',
         b BIT(1) PATH '$'
       )
     ) AS jt
ORDER BY ord;
-- 1	  0	1    1
-- 2	  1	1    1
{code}
For the first row of the results, I expect it should be 1 0 0 0, as the first row of the table is 0.
