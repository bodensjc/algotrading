library(keras)
library(tidyverse)
library(readr)
library(tibble)

learning_data <- read_csv("learning_data.csv")

price = learning_data[1]

train_data <- as_data_frame(learning_data[1:500,])
val_data <- s_data_frame(learning_data[501:800,])
test_data <- s_data_frame(learning_data[801:966,])

train_data$time


ggplot()+
  geom_line(aes(x=train_data$time, y=train_data$close, group=1),color="red")+
  geom_line(aes(x=val_data$time, y=val_data$close, group=1),color="black")+
  xlab("Time")+ylab("ADA price (USD)")+
  geom_line(aes(x=test_data$time, y=test_data$close, group=1),color="blue")
