# 删除重复条目

    DELETE FROM na_ip_domain
    WHERE id NOT IN (
        SELECT * FROM (
            SELECT MIN(id)
            FROM na_ip_domain
            GROUP BY domain, ip, port
        ) AS subquery
    );