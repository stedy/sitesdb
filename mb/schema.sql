DROP TABLE IF EXISTS demo;
CREATE TABLE demo (subject_ID text, pt_init text, Name text, uwid text,
                    Status text, txdate text, Donrep text);

DROP TABLE IF EXISTS recipient_swabs;
CREATE TABLE recipient_swabs (subject_ID text, Expected_pre_tx date, Received_pre_tx date,
                    Expected_week1 date, Actual_week1 date,
                    Expected_week2 date, Actual_week2 date,
                    Expected_week3 date, Actual_week3 date,
                    Expected_week4 date, Actual_week4 date,
                    Expected_week5 date, Actual_week5 date,
                    Expected_week6 date, Actual_week6 date,
                    Expected_week7 date, Actual_week7 date,
                    Expected_week8 date, Actual_week8 date,
                    Expected_week9 date, Actual_week9 date,
                    Expected_week10 date, Actual_week10 date,
                    Expected_week11 date, Actual_week11 date,
                    Expected_week12 date, Actual_week12 date,
                    Expected_week13 date, Actual_week13 date,
                    Expected_week14 date, Actual_week14 date);

DROP TABLE IF EXISTS donor_swabs;
CREATE TABLE donor_swabs (subject_ID text, Expected_pre_tx date, Received_pre_tx date,
                    Expected_week1 date, Actual_week1 date,
                    Expected_week2 date, Actual_week2 date,
                    Expected_week3 date, Actual_week3 date,
                    Expected_week4 date, Actual_week4 date,
                    Expected_week5 date, Actual_week5 date,
                    Expected_week6 date, Actual_week6 date,
                    Expected_week7 date, Actual_week7 date,
                    Expected_week8 date, Actual_week8 date,
                    Expected_week9 date, Actual_week9 date,
                    Expected_week10 date, Actual_week10 date,
                    Expected_week11 date, Actual_week11 date,
                    Expected_week12 date, Actual_week12 date,
                    Expected_week13 date, Actual_week13 date,
                    Expected_week14 date, Actual_week14 date);

DROP TABLE IF EXISTS recipient_blood;
CREATE TABLE recipient_blood (subject_ID text, Blood_draw_pre_tx date, Received_pre_tx date,
                    Pre_tx_time_drawn text, Pre_td_time_processed text,
                    Expected_week1 date, Actual_week1 date,
                    Week1_time_drawn text, Week1_time_processed text,
                    Expected_week2 date, Actual_week2 date,
                    Week2_time_drawn text, Week2_time_processed text,
                    Expected_week3 date, Actual_week3 date,
                    Week3_time_drawn text, Week3_time_processed text,
                    Expected_week4 date, Actual_week4 date,
                    Week4_time_drawn text, Week4_time_processed text);

DROP TABLE IF EXISTS donor_blood;
CREATE TABLE donor_blood (subject_ID text, Blood_draw_pre_tx date, Received_pre_tx date,
                    Pre_tx_time_drawn text, Pre_td_time_processed text,
                    Expected_week1 date, Actual_week1 date,
                    Week1_time_drawn text, Week1_time_processed text,
                    Expected_week2 date, Actual_week2 date,
                    Week2_time_drawn text, Week2_time_processed text,
                    Expected_week3 date, Actual_week3 date,
                    Week3_time_drawn text, Week3_time_processed text,
                    Expected_week4 date, Actual_week4 date,
                    Week4_time_drawn text, Week4_time_processed text);

DROP TABLE IF EXISTS user;
CREATE TABLE user (name text, user_id text);
