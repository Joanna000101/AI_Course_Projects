#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages com.databricks:spark-xml_2.12:0.14.0 pyspark-shell'


# In[2]:


from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()


# In[17]:


from pyspark.sql.types import StructType, StructField, StringType, FloatType
from pyspark.sql.functions import desc


# In[5]:


fp="gs://hw2_bucketwb/notebooks/jupyter/task2samllfull.csv"
df = spark.read.options(header='False', inferSchema=True, delimiter='\t').csv(fp)
df.printSchema()


# In[7]:


df2 = df.withColumnRenamed('_c0','title').withColumnRenamed('_c1','link')
df2.show(10)


# In[13]:


# convert DataFrame to RDD
title_links = df2.rdd.map(lambda item:(item['title'], item['link'])).distinct().groupByKey().cache()
title_rank = title_links.map(lambda title: (title[0], 1.0))
# title_rank.take(1)


# In[14]:


# title_links.join(title_rank).take(1)


# In[16]:


n = 10
for i in range(n):
    contributions = title_links.join(title_rank)    .flatMap(lambda title_links_rank:    [(link, title_links_rank[1][1] / len(title_links_rank[1][0])) for link in title_links_rank[1][0]])
    
    title_rank = contributions.reduceByKey(lambda cont1, cont2: cont1 + cont2)    .mapValues(lambda cont: 0.15 + 0.85 * cont)


# In[18]:


schema_df3 = StructType([StructField("article", StringType(), True), StructField("rank", FloatType(), True)])

# convert RDD to DataFrame
df3 = spark.createDataFrame(title_rank, schema_df3)
df4 = df3.sort(desc("rank")).limit(10)
df4.show(10)


# In[ ]:


df4.repartition(1).write.mode("overwrite").csv("gs://hw2_bucketwb/notebooks/jupyter/task3.csv",header=False,sep='\t')

