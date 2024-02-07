# Variables
# day = Time 
# phys_dist_km = Spatial Distance (numerical)
# phys_dist_5cat = Spatial Distance (categorical)
# VADER_sentiment = Sentiment

# Imports
library(MASS)
library(dplyr)
library(ggplot2)
library(car)
library(mgcv)
library(rgl)

# Load data
#tweets <- read.csv('Tweets_final.csv', stringsAsFactors=FALSE)
tweets <- read.csv("D:/UNI/BC Thesis/GeoCOV Data/6 final/tweets_R.csv", stringsAsFactors=FALSE)

# Factor distance
tweets$phys_dist_5cat <- factor(tweets$phys_dist_5cat, ordered=T,
                                levels = c("Close", "Bordering", "Regional", 'Continental', 'Global'))

#------------------------------Attention-------------------------------------------

# Tweet activity variable aggregated by day and Distance
tweets_freq <- tweets %>% count(day, phys_dist_km)

# Try Poisson first and check overdispersion
library(AER)
pois <- glm(n ~ phys_dist_km + day, data=tweets_freq, family=poisson)
dispersiontest(pois) # Overdispersed

# Negative Binomial Regression instead
library(VGAM)
nb0 <- vglm(n ~ 1, family = negbinomial(), data = tweets_freq, trace=T, model=T)
nb1 <- vglm(n ~ day, family = negbinomial(), data = tweets_freq, trace=T, model=T)
nb2 <- vglm(n ~ phys_dist_km + day, family = negbinomial(), data = tweets_freq, trace=T, model=T)
summary(nb0)
summary(nb1)
summary(nb2)

# Exponentiate coefs
exp(coefvlm(nb1))
exp(coefvlm(nb2))

# Compare models
#Likelihood-ratio test
lrtest(nb0, nb1, nb2)
# AIC
AICvlm(nb0)
AICvlm(nb1)
AICvlm(nb2)



#--------------------------SENTIMENT---------------------------------------


## Sentiment
# Final stepwise regression
lm1 <- lm(VADER_sentiment ~ day, data = tweets)
lm2 <- lm(VADER_sentiment ~ phys_dist_km + day, data = tweets)
lm3 <- lm(VADER_sentiment ~ poly(phys_dist_km,2)+poly(day,4), data = tweets)
summary(lm1, digits=4)
summary(lm2, digits=4)
summary(lm3, digits=4)
anova(lm1, lm2, lm3)

# Standardized Coeffs: to compare predictors
library(QuantPsyc)
lm.beta(lm1)
lm.beta(lm2)
lm.beta(lm3)

## Regression assumptions 
## Coded by Regorz Statistics: http://www.regorz-statistik.de/en/r_testing_regression_assumptions.html
#Loading necessary packages
library(olsrr)
library(jtools)
library(moments)
library(lmtest)

# Random sample 5k
slice_sample(tweets, n = 5000)

# Linear regression
reg.fit <- lm(VADER_sentiment ~ phys_dist_km + day, data = tweets)
par(mfrow = c(2, 2))
plot(reg.fit) # Assumption checks

# Parameters for the regression output
my_confidence <- 0.95
my_digits <- 3
# Data for the linearity check
attach(tweets_freq)
daten.plot <- data.frame(n, phys_dist_km, day)
detach(tweets_freq)

# 1 Regression output (with jtools package)
# 1.1 Unstandardized results
summ(reg.fit, confint=TRUE, ci.width = my_confidence,
     digits = my_digits)
# 1.2 Standardized results
summ(reg.fit, scale=TRUE, transform.response = TRUE, digits=my_digits)

# 2 Regression diagnostics (with olsrr package, unless otherwise specified)
# 2.1 Homoskedasticity
# 2.1.1 Graphical test
# (should be a chaotic point cloud; problematic especially
# a funnel shape or a recognizably curved structure)
ols_plot_resid_fit(reg.fit)
# 2.1.2 Breusch Pagan Test - Signifikance test for heteroskedasticity
# (significant => heteroskedasticity)
ols_test_breusch_pagan(reg.fit)

# 2.2 Normality of the residuals
# 2.2.1 Histogram of residuals
# (The histogramm should show a normal
# distribution,
# especially at the tails of the distribution)
ols_plot_resid_hist(reg.fit)
# 2.2.2 QQ plot
# (The data points should be near the diagonal)
ols_plot_resid_qq(reg.fit)
# 2.2.3 Shapiro-Wilk test for normality
# (significant => residuals not normally distributed)
shapiro.test(reg.fit$residuals)
# 2.2.4 Skewness and kurtosis (with moments package)
#(For normality skewness near 0 and kurtosis near 3)
skewness(reg.fit$residuals)
kurtosis(reg.fit$residuals)
# 2.2.5 Significance tests for skewness and kurtosis
#(with moments-Package)
#(significant => residuals not normally distributed)
agostino.test(reg.fit$residuals)
anscombe.test(reg.fit$residuals)

# 2.3 Linearity
# 2.3.1 Pairwise scatterplots
# (Only the scatterplots including the criterion
# variable are relevant)
pairs(daten.plot, pch = 19, lower.panel = NULL)
# 2.3.2 Rainbow test (with lmtest-Package) for linearity
# (significant => nonlinearity)
raintest(reg.fit)

# 2.4 Absence of strong multicollinearity
# (Problematic: VIF values above 10.0)
ols_vif_tol(reg.fit)

# Normality assumption on 1k samples of 5k (max allowed by Shapiro Test)
pv <- replicate(10^3, 
                shapiro.test(
                  lm(VADER_sentiment ~ phys_dist_km+day, data=slice_sample(tweets, n = 5000))$residuals
                )$p.val)
# How many samples were non-normal?
mean(pv <= .05)


##  ANCOVA

# Max day per category 
aggregate(day ~ phys_dist_5cat, data = tweets, max)
# No global tweets after day 35, so limit analysis to <=35
tweets <- tweets[tweets$day<=35,] 
# Descriptives
tweets %>% count(phys_dist_5cat) # Group sizes
aggregate(VADER_sentiment ~ phys_dist_5cat, tweets, FUN=function(x) c(M=mean(x), SD=sd(x))) # Mean, SD

# Parametric Assumptions: Non-normality and slopes not met
leveneTest(VADER_sentiment ~ phys_dist_5cat, tweets)
ggplot(tweets, aes(day, VADER_sentiment, color = phys_dist_5cat)) + 
  geom_smooth(method='lm', se=FALSE) 

## Non-parametric ANCOVA: Quade's Ranked
# Assumption: covariate is distributed similar per group
ggplot(tweets, aes(x = day)) + 
  geom_histogram(bins=max(tweets$day)) + facet_wrap(~ phys_dist_5cat) +
  ylab('Number of Tweets') +
  xlab('Days into pandemic')
# 1. Rank order DV and COV
tweets$sentR <- rank(tweets$VADER_sentiment)
tweets$dayR <- rank(tweets$day)
# 2. Linear regression on ranked DV with ranked COV as predictor
model <- lm(sentR ~ dayR, data=tweets)
# 2.5 Save unstandardized residuals
res <- model$residuals
# 3. ANOVA on unstd res. with distance as IV.
ancova <- aov(res ~ tweets$phys_dist_5cat)
# Interpret output like normal ANOVA
summary(ancova, digits=3)
# All in 1 line
summary(ancova <- aov(lm(rank(VADER_sentiment) ~ rank(day), tweets)$residuals ~ phys_dist_5cat, tweets))
# Post-hocs
library(multcomp)
library(DescTools)
#TukeyHSD(ancova) # Tukey
ScheffeTest(ancova) # Scheffe, better for unequal group sizes
# Effect size eta2: ~0.02=small, ~0.13=medium, ~0.26=large
EtaSq(ancova)

#--------------------------------FIGURES-----------------------------------------

# Fig. 1: made in Illustrator
# Fig. 3: made in Python + Illustrator

# Fig. 4: 3D plot
# Manual approach: Interpolation + Persp()
# Create data
x <- seq(0,57,by=1)
y <- seq(0,6000,by=100)

# Interpolate
model <- gam(VADER_sentiment ~ s(phys_dist_km, bs='tp') + s(day, bs='tp'), data=tweets) # Thin-plate splines, penalized
z <- predict(model, newdata=expand.grid(day=x, phys_dist_km=y)) 

# Color by height: red to green gradient for Sentiment
jet.colors <- colorRampPalette( c("red", "green") ) 
pal <- jet.colors(100)
col.ind <- cut(z,100) # colour indices of each point

# Plot
persp3d(x, y, z,
        front='lines', back="lines", col='black',
        zlab="Sentiment", ylab = "Distance (km)", xlab="Time (days)",
        zlim=c(-0.1, 0.2), #ylim=c(0,6000), xlim=c(0,57),
        box=F, axes=T, specular="black")
surface3d(x, y, z, col=pal[col.ind], shade=0.4, shininess=80)
axis3d(edge='z+-') 
# Save plot
rgl.postscript("Fig3.svg", fmt="svg")

## Fig 4. Sentiment over time per distance cat
library("RColorBrewer")
# Smoothed
fig4 <- tweets %>% #[tweets$day<=35,]
  ggplot(aes(x=day, y=VADER_sentiment, color=phys_dist_5cat)) +
  ylab("Sentiment") +
  xlab("Time (days)") +
  labs(color='Distance') +
  #scale_color_brewer(palette="Dark2") +
  geom_smooth(span=0.1, se=F) #default span=0.75

library(svglite)
ggsave(file="Fig4.svg", plot=fig4, width=10, height=8)
