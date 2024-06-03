#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages com.databricks:spark-xml_2.12:0.14.0 pyspark-shell'

import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, lower, explode
from pyspark.sql.types import StringType, ArrayType


# In[2]:


# Create Spark Session from Builder
spark = SparkSession.builder.getOrCreate()


# In[3]:


# input file
fp = 'hdfs:/wiki-small.xml'
# create a DataFrame
df = spark.read.format('xml').options(rowTag='page').load(fp)
# print schema
df.printSchema()


# In[4]:


df1 = df.withColumn("text", lower(col("revision.text._VALUE"))).withColumn("title", lower(col("title"))) .select("title", "text")
df1.show()


# In[5]:


# an UDF to extract links from "revision" columns and return a list of 
def extract_links(text):
    # this regex handles all situations needed except the all whitespace or empty string case
    pattern = '(?<=\[\[)((?:category:)[^#\|\]]*?|[^#\|\]:]*?)(?=\||\]\])'
    links = re.findall(pattern, text, flags=re.I | re.M)
    # filter out empty strings and strings with all whitespaces
    non_empty = [l for l in links if not l.isspace() and len(l)>0]
    return non_empty

extract_links_udf = udf(extract_links, ArrayType(StringType()))


# In[6]:


# REGEX testing
# text = "[[    ]][[]][[File:Hercules Musei Capitolini MC1265 n2.jpg|thumb|right|upright|[[Heracles]] with the apple of [[Hesperides]]]]"
# pattern = '(?<=\[\[)((?:category:)[^#\|\]]*?|[^#\|\]:]*?)(?=\||\]\])'
# links = re.findall(pattern, text, flags=re.I | re.M)

# print(links)


# In[7]:


# Explode the links list
df2 = df1.withColumn("links", extract_links_udf(col("text"))).withColumn("link", explode("links")).drop("links", "text")
# Sort two columns in Ascending order, and limit to 10 rows
df3 = df2.sort("title", "link").limit(10)
df3.show()


# In[8]:


df3.write.mode("overwrite").csv("gs://4121-programming2/notebooks/jupyter/task2.csv",header=False,sep='\t')


# In[ ]:




