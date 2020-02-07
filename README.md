# Insight Data Engineering - Safer Travel Plan

## Table of Contents
1. General Info
1. Programming Language & Tools
1. Data Description
1. Under the Hood
1. Tech Stack
1. Engineering Challenge

## General Info

This is for Insight Data Engineering project - Safer Travel Plan. Violent crime in the United States is always a big issue for travelers and the number of reported violent crimes in the United States has risen in the past few years. In 2018, the crime rate (the number of reported instances per 100,000 inhabitants) was 382.9 for overall violent crime. It is important to note that violent crime rates may not always be precise as crimes that remain unreported can often skew rates meaning it can generally be assumed that instances of crime are more prevalent than reported crime statistics suggest.

However, traveling is becoming more and more popular for people to enjoy life and explore the world. It's extremely important to keep safe while enjoying traveling. That's one of the reasons why travel plan is important, it can push people to do more research before hit the road. Dates, areas, cities play important roles to keep travelers safe. Therefore this project aims to create a platform for travelers to provide safety suggestions based on crime datasets from 15 US cities. This platform would be pretty helpful for people who are new to a city and want to get more info about safety.

This paltform is also versatile to track other time-based features, like finantial products, statistics of Oil & Gas, etc.

## Programming Language & Tools
Programming language: python3
Tools: Amazon S3, Apache Spark, PostgreSQL, Dash

## Data Description
* Crime Data of 15 cities in the US from government websites
* csv files

## Under the Hood
* Stored the seperate csv files into Amazon S3, combined and processed them in Apache Spark, then store the final database on PostgreSQL
* Applied time series models to predict the crime amount for a sepecified city and time range
* Built a user-friendly dashboard to provide suggestions about safer dates, time and areas for travelers
  
## Tech Stack
![Image of Tech Stack](https://github.com/Carinaup/Insight_DE_Music_Fingerprinting/blob/master/images/techstack.png)

## Engineering Challenge
* How to accelarate the process of loading results on dashboard
           
