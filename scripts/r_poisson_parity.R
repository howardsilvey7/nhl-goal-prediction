# Base R counterpart to the final independent Poisson fit. No add-on packages.
args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) args[1] else "."
f <- read.csv(file.path(root, "data/processed/features.csv"))
numeric_names <- c("is_home","team_gf","team_ga","opp_gf","opp_ga",
 "team_sf","team_sa","opp_sf","opp_sa","team_cf","opp_ca","rest",
 "opp_rest","history_n","league_rate")
stack <- function(f) {
 blocks <- lapply(c("home","away"), function(side) {
  other <- if (side=="home") "away" else "home"
  get <- function(s,n) f[[paste0(s,"_",n)]]
  data.frame(game_id=f$game_id,season=f$season,target=get(side,"goals"),
   is_home=as.numeric(side=="home"),team_gf=get(side,"gf"),team_ga=get(side,"ga"),
   opp_gf=get(other,"gf"),opp_ga=get(other,"ga"),team_sf=get(side,"sf"),
   team_sa=get(side,"sa"),opp_sf=get(other,"sf"),opp_sa=get(other,"sa"),
   team_cf=get(side,"cf"),opp_ca=get(other,"ca"),rest=get(side,"rest"),
   opp_rest=get(other,"rest"),history_n=get(side,"history_n"),
   league_rate=f[[paste0("league_",side)]])
 })
 do.call(rbind,blocks)
}
train <- stack(f[f$season<2024,])
test <- stack(f[f$season==2024,])
x <- as.matrix(train[,numeric_names]); y <- train$target
center <- colMeans(x)
scale <- sqrt(colMeans(sweep(x,2,center,"-")^2))
scale[scale==0] <- 1
z <- cbind(1,sweep(sweep(x,2,center,"-"),2,scale,"/"))
zt <- cbind(1,sweep(sweep(as.matrix(test[,numeric_names]),2,center,"-"),2,scale,"/"))
# Frozen Python penalty is alpha=1. Mean Poisson likelihood + L2/2.
alpha <- 1
objective <- function(beta) {
 eta <- as.vector(z %*% beta)
 mean(exp(eta)-y*eta)+alpha*sum(beta[-1]^2)/2
}
gradient <- function(beta) {
 eta <- as.vector(z %*% beta)
 as.vector(crossprod(z,exp(eta)-y))/length(y)+c(0,alpha*beta[-1])
}
initial <- c(log(mean(y)),rep(0,ncol(z)-1))
fit <- optim(initial,objective,gradient,method="BFGS",control=list(maxit=2000,reltol=1e-12))
stopifnot(fit$convergence==0)
mu <- exp(as.vector(zt %*% fit$par))
n <- nrow(test)/2
joint_nll <- mean(-dpois(test$target[1:n],mu[1:n],log=TRUE)-
                 dpois(test$target[(n+1):(2*n)],mu[(n+1):(2*n)],log=TRUE))
mae <- mean(abs(test$target-mu))
metrics <- read.csv(file.path(root,"reports/holdout-metrics.csv"))
expected <- metrics[metrics$model=="poisson",]
stopifnot(abs(joint_nll-expected$joint_nll)<1e-6, abs(mae-expected$combined_mae)<1e-6)
out <- data.frame(r_version=R.version.string,model="poisson",joint_nll=joint_nll,
 combined_mae=mae,nll_absolute_difference=abs(joint_nll-expected$joint_nll),
 mae_absolute_difference=abs(mae-expected$combined_mae),tolerance=1e-6)
write.csv(out,file.path(root,"reports/r-parity.csv"),row.names=FALSE)
writeLines(capture.output(sessionInfo()),file.path(root,"reports/r-session.txt"))
print(out)
