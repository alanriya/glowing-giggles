DELETE_RAW_DATA_REQUEST = """
            DELETE FROM category;
            DELETE FROM categorylinks;
            DELETE FROM page;
            DELETE FROM pagelinks;
            DELETE FROM templatelinks;
        """

CREATE_METADATA_REQUEST = """
            DROP TABLE IF EXISTS `pagemetadata`;
            CREATE TABLE `pagemetadata` (
                `page_title` varbinary(255) NOT NULL DEFAULT '',
                `category` varbinary(255) NOT NULL DEFAULT '',
                `last_updated` timestamp NOT NULL
            )
        """

LOAD_METADATA_REQUEST = """
        INSERT INTO `pagemetadata`
        select
            a.page_title,
            b.cl_to as category,
            STR_TO_DATE( a.page_touched, '%Y%m%d%H%i%s') last_updated
        from
            (
            select
                *
            FROM
                page) a
        left join (
            select
                *
            FROM
                categorylinks) b ON
            a.page_id = b.cl_from
        WHERE
            b.cl_from is not null;
        """
    
CREATE_PAGE_LINK_REQUEST = """
            DROP TABLE IF EXISTS `pagelinkdata`;
            CREATE TABLE `pagelinkdata` (
                `page` varbinary(255) NOT NULL,
                `referredpage` varbinary(255) NOT NULL,
                `position` INT NOT NULL
            );"""
        
PAGE_LINK_DATA_REQUEST = """
    INSERT INTO `pagelinkdata`
    select
        page,
        referredpage ,
        RANK() OVER (PARTITION BY page ORDER BY referredpage) as `position`
    from
    (
        select
            tl.tl_title page,
            p.page_title referredpage
        from
            templatelinks tl
        LEFT JOIN page p ON
            tl.tl_from = p.page_id
        WHERE p.page_title is not null
        order by tl.tl_title
    ) a
    """

CREATE_LINK_DATA_REQUEST = """
            DROP TABLE IF EXISTS `linkcounttable`;
            CREATE TABLE `linkcounttable` (
                `page` varbinary(255) NOT NULL,
                `count` int NOT NULL
            );"""
                  
LOAD_LINK_COUNT_REQUEST = '''
    INSERT INTO linkcounttable 
    SELECT a.page page, count(*) as `count` FROM (select
        tl.tl_title page,
        p.page_title referredpage
    FROM
        templatelinks tl
    LEFT JOIN page p ON
        tl.tl_from = p.page_id) a group by a.page;
    '''
    
CREATE_OUTDATED_PAGE_REQUEST = """
            DROP TABLE IF EXISTS `outdatedpagedata`;
            CREATE TABLE `outdatedpagedata` (
                `page` varbinary(255) NOT NULL,
                `referredpage` varbinary(255) NOT NULL,
                `pagelastupdated` timestamp,
                `category` varbinary(255),
                `referredlastupdated` timestamp,
                `difference` DECIMAL(19,9)
            );"""
    
OUTDATED_PAGE_REQUEST = """
    INSERT INTO `outdatedpagedata`
    SELECT
        c.page,
        c.referredpage,
        c.page_last_updated,
        c.category ,
        d.last_updated as referred_last_updated,
        (d.last_updated-c.page_last_updated)/ 60 / 60 / 24 as difference
    FROM
        (
        select
            a.page,
            a.referredpage,
            b.last_updated page_last_updated,
            b.category
        from
            pagelinkdata a
        LEFT JOIN (
            select
                DISTINCT(page_title),
                last_updated,
                category
            from
                pagemetadata) b on
            a.page = b.page_title) as c
    LEFT JOIN (
        select
            page_title,
            max(last_updated) as last_updated
        from
            pagemetadata
        group by
            page_title) d ON
        c.referredpage = d.page_title
    WHERE
        c.category is not null
        and c.page_last_updated is not null
        and d.last_updated is not null"""
        
CREATE_OUTDATED_DIFF_PAGE_REQUEST = """
    DROP TABLE IF EXISTS `mostoutdatedpage`;
    CREATE TABLE `mostoutdatedpage` (
        `page` varbinary(255) NOT NULL,
        `category` varbinary(255) NOT NULL
    );"""
        
OUTDATED_PAGE_BY_CATEGORY_REQUEST = """
    INSERT INTO `mostoutdatedpage`
    SELECT
        tbl1.page, tbl1.category
    FROM
        outdatedpagedata tbl1
    INNER JOIN (
        select
            max(difference) as maxdiff,
            category
        from
            (
            select
                *
            from
                outdatedpagedata
            ) a
        group by
            a.category) tbl2
    ON
        tbl1.category = tbl2.category
        AND tbl1.difference = tbl2.maxdiff
    ORDER BY
        tbl2.maxdiff DESC"""