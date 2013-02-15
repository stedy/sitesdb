#create some fake data for testing edge cases
#200 cases
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

final <- data.frame(irs.id, proj.id, proj.tube.no, proj.cell, 
                   date.out, shipped.to,
                   sent.to, received.logical)
write.csv(final, "test_sampleFlow.csv", row.names=F)