#create some fake data for testing edge cases
#start with sample movement
irs.id <- c(paste0("IDS-000000", 1:9), 
            paste0("IDS-00000", 10:99), paste0("IDS-0000", 100:200))
proj.id <- rep(paste0("IDS-00", 1:8), times = 25)
proj.cell <- round(abs(rnorm(100, sd=30)))
proj.tube.no <- round(abs(rnorm(100, sd=60, mean=50)))
Start <- as.Date("2010-01-01")
End <- as.Date("2013-01-31")
date.out <- Start + sample.int(End-Start, 200)
names <- c("not yet shipped", "NA", "Jane Kuypers", "Meei-Li Huang", 
           "Frodo Baggins", "Bilbo Baggins", "Meriadoc Brandybuck",
           "Gimli son of Gloin", "Peregrin Took",
           "Gandalf the Grey", "Aragorn", 'Boromir')
shipped.to <- sample(names, 200, replace=T)
places <- c("aliquoted in house", "Molecular Diagnostics", "The Shire", 
            "Lothlorien", "Rivendell", "Isengard",
            "Rohan", "Iron Hills")
sent.to <- sample(places, 200, replace=T)
received <- date.out + sample.int(200)
received.logical <- ifelse(received > Sys.Date(), NA, received)
class(received.logical) <- "Date"

sampleFlow <- data.frame(irs.id, proj.id, proj.tube.no, proj.cell, 
                   date.out, shipped.to,
                   sent.to, received.logical)
write.csv(sampleFlow, "test_sampleFlow.csv", row.names=F)

#then do info for each sample

ptdon <- sample(c("pt", "dnr"), 200, replace=T)
sample.res <- sample(c("clinical", "research"), 200, replace=T)
sample.type <- sample(c("serology", "HLA", "954", "ANT", "PCR"), 200, replace=T)
source.collection <- sample(c("whole blood", "serum", "plasma"), 200, replace=T)
sample.acc <- paste0(sample(LETTERS),  round(rnorm(200, mean=20000, sd = 5000)))
collection.date <- Start - sample.int(End-Start, 200)
patient.names <-  sample(c("Animal", "Beaker", "Beauregard", "Camilla the Chicken",
                    "Fozzie Bear", "George the Janitor ", "Kermit",
                    "Lew Zealand", "Link Hogthrob", "Pops", "Rizzo",
                    "Gonzo", "Rowlf", "Waldorf", "Statler",
                    "Swedish Chef", "Scooter"), 200, replace=T)
tx1date <- collection.date - 1
donor.names <- sample(c("Harry Potter", "Hermione Granger", "Ron Weasley",
                        "Ginny Weasley", "Albus Dumbledore", "Severus Snape",
                        "Luna Lovegood", "Moaning Mona",
                        "Hagrid"), 200, replace = T)
signed9 <- sample(c("Y", "N"), 200, prob=c(.9, .5), replace=T)

patient.info <- data.frame(irs.id, ptdon, sample.res, sample.type, source.collection,
                           sample.acc, collection.date, patient.names,
                           tx1date, donor.names, signed9)
write.csv(patient.info, "test_patientInfo.csv", row.names=F)
