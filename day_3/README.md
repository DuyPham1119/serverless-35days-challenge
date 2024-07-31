# Amazon DynamoDB

## Part 1: Introduction to DynamoDB and NoSQL

Compare NoSQL and SQL

| _                 | SQL                                |  noSQL                    |
| :---              |     :---:      |          ---: |
| Data model        | Relational, structured data in tables with predefined schemas |  Various models including document, key-value wide-column, and graph     |
| Schema            | Fixed schema                                                  | Dynamic or flexible schema      |
| Scalability       |  Typically scales vertically       | Designed for horizontal scalability   |
| ACID compliance   | Strongly ACID compliant       | Often sacrifices ACID for performance and scalability      |
| Query language    | Standardized SQL       | Database-specific query languages      |
| Consistency       | Strong consistency       | Often eventual consistency, with some offering strong consistency      |
| Use cases         | Complex queries, transactions       | High volume data, real-time web apps, big data applications      |

DyanmoDB fundamentals

- Tables: The primary structures for storing data in DynamoDB.
- Items:
    - Contained within tables (zero or more per table)
    - Represent uniquely identifiable groups of attributes
    - Similar to rows, records, or tuples in other database systems
    - No limit to the number of items per table
- Attributes:
    - Components of items
    - Represent fundamental, indivisible data elements
    - Similar to fields or columns in other database systems
    - Examples: For a "People" table: PersonID, LastName, FirstName
- Primary Keys: Used to uniquely identify each item in a table
    - Partition key: 
        - A simple primary key, composed of one attribute known as the partition key.
    - Partition key and sort key: 
        - Referred to as a composite primary key, this type of key is composed of two attributes. The first attribute is the partition key, and the second attribute is the sort key.
        - The partition key => hash attribute, The sort key => range attribute
- Secondary indexes:
    - Global secondary index: An index with a partition key and sort key that can be different from those on the table.
        - Support eventual consistency only
        - Can create up to 20 GSIs per table
        - GSIs consume additional write capacity units (WCUs) and read capacity units (RCUs)
        - Updates to the base table are asynchronously propagated to the GSI

    - Local secondary index: An index that has the same partition key as the table, but a different sort key.
        - Cannot add a local secondary index to an existing table
        - can create up to 5 LSIs per table
        - Cannot span across partitions (unlike GSIs)
        - Limited to 10 GB per partition key value
        - Shares throughput with underlying table

- Data Types: 
    - Scalar Types: Number, string, binary, Boolean, and null.
    - Document Types: list, map
    - Set Types: string set, number set, and binary set

- Capacity Modes: 
    - Provisioned Capacity Mode:
        - You specify the number of reads and writes per second your application needs
        - Measured in Read Capacity Units (RCUs) and Write Capacity Units (WCUs)
        - You're charged for the provisioned capacity whether you use it or not
        - Can use Auto Scaling to automatically adjust capacity based on usage patterns
    - On-Demand Capacity Mode:
        - DynamoDB automatically scales to accommodate your workloads
        - You pay per request, for only what you use
        - No need to specify or manage capacity units
        - Useful for unpredictable workloads or new applications with unknown usage patterns

- Consistency Models:
    - Eventually Consistent Reads:
        - Default read model
        - Faster but may not reflect the most recent write operation
        - Typically provide consistency within a second
    - Strongly Consistent Reads:
        - Always reflect the most up-to-date data
        - Might have higher latency
        - Consume more read capacity units (RCUs)

    - Performance and cost considerations:
        - Eventually consistent reads use fewer resources and are generally faster
        - Strongly consistent reads use twice the RCUs of eventually consistent reads
        - Choose based on your application's specific requirements for data freshness and performance

    - Use cases:
        - Eventually Consistent: Social media feeds, product catalogs
        - Strongly Consistent: Financial transactions, real-time gaming leaderboards


## Part 2: Hands-On with DynamoDB

Create DynamoDB by cli:

```
aws dynamodb create-table \
    --table-name Music \
    --attribute-definitions \
        AttributeName=Artist,AttributeType=S \
        AttributeName=SongTitle,AttributeType=S \
    --key-schema \
        AttributeName=Artist,KeyType=HASH \
        AttributeName=SongTitle,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=10,WriteCapacityUnits=5 \
    --table-class STANDARD

```

Create record by cli:

```
aws dynamodb put-item \
    --table-name Music  \
    --item \
        '{"Artist": {"S": "No One You Know"}, "SongTitle": {"S": "Call Me Today"}, "AlbumTitle": {"S": "Somewhat Famous"}, "Awards": {"N": "1"}}'
```

Read record by cli

```
aws dynamodb get-item --consistent-read \
    --table-name Music \
    --key '{ "Artist": {"S": "Acme Band"}, "SongTitle": {"S": "Happy Day"}}'
```

Update record by cli:

```
aws dynamodb update-item \
    --table-name Music \
    --key '{ "Artist": {"S": "Acme Band"}, "SongTitle": {"S": "Happy Day"}}' \
    --update-expression "SET AlbumTitle = :newval" \
    --expression-attribute-values '{":newval":{"S":"Updated Album Title"}}' \
    --return-values ALL_NEW
```

Query data:

```
aws dynamodb query \
    --table-name Music \
    --key-condition-expression "Artist = :name" \
    --expression-attribute-values ​​'{":name":{"S":"Acme Band"}}'
```

Create GSIs:

```
aws dynamodb update-table \
    --table-name Music \
    --attribute-definitions AttributeName=AlbumTitle,AttributeType=S \
    --global-secondary-index-updates \
        "[{\"Create\":{\"IndexName\": \"AlbumTitle-index\",\"KeySchema\":[{\"AttributeName\":\"AlbumTitle\",\"KeyType\": \"HASH\"}], \
        \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 10, \"WriteCapacityUnits\": 5 },\"Projection\":{\"ProjectionType\":\"ALL\"}}}]"
```

Query GSIs:

```
aws dynamodb query \
    --table-name Music \
    --index-name AlbumTitle-index \
    --key-condition-expression "AlbumTitle = :name" \
    --expression-attribute-values ​​'{":name":{"S":"Somewhat Famous"}}'
```

## Part 3: Mini Project - Serverless Product Catalog

Check `/mini_project`

## Part 4: Research: Advanced DynamoDB Concepts

### Data Modeling Patterns:

#### Single Table Design

Defination: A data modeling approach in DynamoDB that involves storing multiple types of entities in a single table

- Benefits:
    - Simplified data access
    - Reduced API calls (fewer JOINs)
    - Improved performance
    - Cost-effective (fewer tables to manage but not DynamoDB on-demand)

- Challenges:
    - The steep learning curve to understand single-table design;
    - The inflexibility of adding new access patterns;
    - The difficulty of exporting your tables for analytics.

#### Adjacency list design pattern

Dealing with many-to-many relationships in DynamoDB

- Core Idea:
    - Each entity is represented by a partition key.
    - Relationships to other entities are stored as items within that partition, using the target entity's ID as the sort key.

- Benefits:
    - Minimal data redundancy.
    - Efficiently retrieves all entities related to a specific entity.


#### Materialized Views

DynamoDB Graph Data Model

### Query Optimization
#### Parallel scans

Accelerate the retrieval of data from large tables by dividing the scan operation into multiple segments that can be processed concurrently by different workers.

- Key Parameters
    - TotalSegments: The total number of segments to divide the scan into. This value should match the number of workers.
    - Segment: The specific segment assigned to a worker.

- Usecases:
    - The table size is 20 GB or larger.
    - The table's provisioned read throughput is not being fully used.
    - Sequential Scan operations are too slow

- Considerations
    - Complexity: Implementing parallel scans requires additional code and coordination.
    - Error handling: You need to handle potential errors and inconsistencies in the results from different workers.
    - Cost: While parallel scans can improve performance, they might also increase costs due to increased read throughput consumption.

#### Avoiding sudden spikes in read activity

- Reduce page size
- Isolate scan operations

### Global Tables

### DynamoDB Streams

### Transactions
