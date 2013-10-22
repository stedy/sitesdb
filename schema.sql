DROP TABLE IF EXISTS demo;
CREATE TABLE demo (subject_ID text, pt_init text, Name text, uwid text,
                    Status text, txdate text, Donrep text, conditioning_start_date text);

DROP TABLE IF EXISTS recipient_swabs;
CREATE TABLE recipient_swabs (subject_ID text, Expected_pre_tx date, Received_pre_tx date,
                    Expected_week1 date, Received_week1 date,
                    Expected_week2 date, Received_week2 date,
                    Expected_week3 date, Received_week3 date,
                    Expected_week4 date, Received_week4 date,
                    Expected_week5 date, Received_week5 date,
                    Expected_week6 date, Received_week6 date,
                    Expected_week7 date, Received_week7 date,
                    Expected_week8 date, Received_week8 date,
                    Expected_week9 date, Received_week9 date,
                    Expected_week10 date, Received_week10 date,
                    Expected_week11 date, Received_week11 date,
                    Expected_week12 date, Received_week12 date,
                    Expected_week13 date, Received_week13 date,
                    Expected_week14 date, Received_week14 date);

DROP TABLE IF EXISTS donor_swabs;
CREATE TABLE donor_swabs (subject_ID text, 
                    Expected_pre_tx date, Received_pre_tx date);

DROP TABLE IF EXISTS recipient_blood;
CREATE TABLE recipient_blood (subject_ID text, Blood_draw_pre_tx date, Blood_received_pre_tx date,
                    Pre_tx_time_drawn text, Pre_tx_time_processed text,
                    Blood_expected_week1 date, Blood_received_week1 date,
                    Week1_time_drawn text, Week1_time_processed text,
                    Blood_expected_week2 date, Blood_received_week2 date,
                    Week2_time_drawn text, Week2_time_processed text,
                    Blood_expected_week3 date, Blood_received_week3 date,
                    Week3_time_drawn text, Week3_time_processed text,
                    Blood_expected_week4 date, Blood_received_week4 date,
                    Week4_time_drawn text, Week4_time_processed text);

DROP TABLE IF EXISTS donor_blood;
CREATE TABLE donor_blood (subject_ID text, Blood_draw_pre_tx date, Received_pre_tx date,
                    Pre_tx_time_drawn text, Pre_tx_time_processed text);

DROP TABLE IF EXISTS user;
CREATE TABLE user (name text, user_id text);
