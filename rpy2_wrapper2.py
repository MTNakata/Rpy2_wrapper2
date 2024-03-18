import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

pandas2ri.activate()

def aov(df,category,variable):
    ro.r(f"aov_result <- aov({variable} ~ {category},data={df})")
    ro.r("sum_result <- summary(aov_result)")
    ro.r("sum_result <- as.data.frame(sum_result[[1]])")
    result_df = pandas2ri.rpy2py(ro.r["sum_result"])
    result_df_long = result_df.T.reset_index().rename(columns={"index":"params"}).melt(id_vars="params",var_name="category").dropna()
    result_df_long["variable"] = [variable for i in range(len(result_df_long))]
    return result_df_long
    
def oneway(df,category,variable):
    ro.r(f"oneway_result <- oneway.test({variable} ~ {category},data={df})")
    ro.r("oneway_result <- data.frame(pvalue = oneway_result$p.value,statistic = oneway_result$statistic,method = oneway_result$method)")
    result_df = pandas2ri.rpy2py(ro.r["oneway_result"])
    result_df = result_df.T.reset_index().rename(columns={"index":"params","F":"values"})
    result_df["variable"] = [variable for i in range(len(result_df))]
    return result_df
            
def tukeyHSD(df,category,variable):
    ro.r(f"aov_result <- aov({variable} ~ {category},data={df})")
    ro.r("tukey_result <- TukeyHSD(aov_result)")
    ro.r("tukey_result <- data.frame(tukey_result$Species)")
    result_df = pandas2ri.rpy2py(ro.r["tukey_result"])
    result_df = result_df.T.reset_index().rename(columns={"index":"params"})
    result_df_long = result_df.melt(id_vars="params",var_name="pair")
    variable_pairs = pd.DataFrame([p.split("-") for p in result_df_long["pair"]],columns=["var1","var2"])
    result_df_long = pd.concat([result_df_long,variable_pairs],axis=1)
    result_df_long = result_df_long[["params","var1","var2","value"]]
    result_df_long["variable"] = [variable for i in range(len(result_df_long))]
    return result_df_long

def dunnett_test(df,category,variable,control):
    ro.r("library(DescTools)")
    ro.r(f"dunnett_result <- DunnettTest({variable}~{category},data={df},control='{control}')")
    ro.r(f"dunnett_result <- data.frame(dunnett_result${control})")
    result_df = pandas2ri.rpy2py(ro.r["dunnett_result"])
    result_df = result_df.T.reset_index().rename(columns={"index":"params"})
    result_df_long = result_df.melt(id_vars="params",var_name="pair")
    variable_pairs = pd.DataFrame([p.split("-") for p in result_df_long["pair"]],columns=["var1","var2"])
    result_df_long = pd.concat([result_df_long,variable_pairs],axis=1)
    result_df_long = result_df_long[["params","var1","var2","value"]]
    result_df_long["variable"] = [variable for i in range(len(result_df_long))]
    return result_df_long
        
def rpy2_close():
    pandas2ri.deactivate()