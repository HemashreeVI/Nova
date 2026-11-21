// Your resume, boiled down to what job matching needs. Edit it any time in Settings → Profile.

export const DEFAULT_PROFILE = {
  gradYear: 2027,
  level: "student",   // student | fresher | experienced
  roles: [
    "data analyst", "data analytics", "business analyst", "data science", "data engineer",
    "backend", "software engineer", "software developer", "sde", "python developer",
    "machine learning", "ml engineer", "ai engineer", "devops", "site reliability",
  ],
  skills: [
    "python", "java", "sql", "javascript", "html", "css",
    "spring boot", "fastapi", "rest api", "kafka", "postgresql", "redis", "sqlite",
    "docker", "github actions", "ci/cd", "prometheus", "grafana", "opentelemetry", "linux", "git",
    "pytorch", "opencv", "yolo", "llm", "rag", "machine learning", "deep learning", "computer vision",
    "pandas", "numpy", "matplotlib", "data analysis", "data visualization", "statistics", "excel",
    "raspberry pi", "arduino", "iot",
  ],
  locations: ["chennai", "bangalore", "bengaluru", "hyderabad", "remote", "india", "work from home"],
  keywords: ["data analyst intern", "python intern", "backend intern", "machine learning intern"],
};

// Skills the matcher knows how to spot in a job description. Aliases map to one canonical name.
export const SKILL_VOCAB = {
  python: ["python"], java: ["java(?!script)"], sql: ["sql", "mysql", "t-sql", "pl/sql"],
  javascript: ["javascript", "node\\.?js", "typescript"], html: ["html"], css: ["css"],
  "c++": ["c\\+\\+"], r: ["\\br programming", "\\bin r\\b", "rstudio"], scala: ["scala"], go: ["golang"],
  "spring boot": ["spring boot", "spring"], fastapi: ["fastapi"], django: ["django"], flask: ["flask"],
  react: ["react"], "rest api": ["rest(ful)? apis?", "restful"],
  kafka: ["kafka"], spark: ["spark", "pyspark"], hadoop: ["hadoop"], airflow: ["airflow"],
  postgresql: ["postgres", "postgresql"], mongodb: ["mongo", "mongodb"], redis: ["redis"], sqlite: ["sqlite"],
  snowflake: ["snowflake"], bigquery: ["bigquery"], dbt: ["dbt"], etl: ["etl", "elt", "data pipelines?"],
  docker: ["docker"], kubernetes: ["kubernetes", "k8s"], aws: ["aws", "amazon web services"],
  azure: ["azure"], gcp: ["gcp", "google cloud"], linux: ["linux", "unix"], git: ["git", "github"],
  "github actions": ["github actions"], "ci/cd": ["ci/cd", "ci cd", "continuous integration"],
  prometheus: ["prometheus"], grafana: ["grafana"], opentelemetry: ["opentelemetry"],
  pytorch: ["pytorch"], tensorflow: ["tensorflow", "keras"], "scikit-learn": ["scikit", "sklearn"],
  opencv: ["opencv"], yolo: ["yolo"], llm: ["llms?", "large language models?", "genai", "generative ai"],
  rag: ["rag", "retrieval.augmented"], nlp: ["nlp", "natural language"],
  "machine learning": ["machine learning", "\\bml\\b"], "deep learning": ["deep learning"],
  "computer vision": ["computer vision"],
  pandas: ["pandas"], numpy: ["numpy"], matplotlib: ["matplotlib", "seaborn"],
  excel: ["excel", "spreadsheets?", "vlookup", "pivot tables?"], "power bi": ["power ?bi", "dax"],
  tableau: ["tableau"], looker: ["looker"], statistics: ["statistics", "statistical", "hypothesis testing", "a/b test"],
  "data analysis": ["data analysis", "data analytics", "analy[sz]e data", "eda"],
  "data visualization": ["data visuali[sz]ation", "dashboards?"],
  "raspberry pi": ["raspberry pi"], arduino: ["arduino"], iot: ["iot", "internet of things"],
};
