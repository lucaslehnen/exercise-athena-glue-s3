# Exercício usando o S3, Glue e Athena

Exercício da pós de Engenharia de dados:

Você é Engenheiro(a) de Dados em uma grande instituição educacional. O
gestor de sua área iniciou um novo projeto de inteligência de dados com o
objetivo de entender o desempenho de alunos do ensino médio de todo o
Brasil no Exame Nacional do Ensino Médio (ENEM). Desse modo, você será
responsável por construir um Data Lake com os dados do ENEM 2020, realizar
o processamento utilizando ferramental adequado e disponibilizar o dado
para consultas dos usuários de negócios e analistas de BI.
Para a realização dessa atividade, recomenda-se o uso dos serviços AWS.
Contudo, caso prefira, você poderá montar o seu lake e sua estrutura de
processamento de dados em qualquer provedor de nuvem que preferir.

1. Realizar o download dos MICRODADOS do ENEM 2020. O arquivo está
disponível neste link: (https://www.gov.br/inep/pt-br/acesso-ainformacao/dados-abertos/microdados);
2. Criar um bucket chamado datalake-<seunome>-<numerodaconta>
para armazenamento dos dados crus do ENEM 2020;
3. Fazer a ingestão dos dados do ENEM 2020 em seu data lake numa
pasta intitulada raw-data utilizando o SDK de sua preferência ou a AWS
CLI (Boto3 -
https://boto3.amazonaws.com/v1/documentation/api/latest/index.ht
ml; AWS CLI - https://docs.aws.amazon.com/cli/latest/userguide/clichap-welcome.html e
https://awscli.amazonaws.com/v2/documentation/api/latest/index.ht
ml);
4. Fazer a transformação do CSV em parquet utilizando spark;
5. Escrever o parquet em uma outra pasta no bucket chamada consumerzone;
6. Criar e executar um Glue Crawler para disponibilizar o schema dos
dados do ENEM 2020;
7. Realizar consultas SQL no AWS Athena para responder às perguntas

---

## Para replicar o exercício:

Criar o virtual env e instalar as dependências nele:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

As credenciais eu havia configurado anteriormente no AWS CLI, então ao executar o python o boto3 já lê das variáveis de ambiente.
Para fins do exercício, utilizei credenciais com acesso administrador temporárias do IAM.

**Criar o bucket via boto3**

```python
python3 s3_create_bucket.py
```

** Atenção porque ele não cria o bucket com o acesso público bloqueado!

**Ingerir os dados**

O arquivo CSV baixado deve ter 1.9GB. Tem um exemplo aqui no repositório só com o head do mesmo.

Para fazer a prática de ingestão, utilizei o boto3 e segui o guia da documentação: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
Fiz o basicão, no guia mesmo dá pra melhorar muito (colocando progresso, tratamento de erro, etc), mas não é o foco.


** Poderia ser utilizado o Terraform para criar o bucket e fazer a ingestão também. Tentei fazer conforme sugerido pra simplificar e exercitar o python.

**Criar o Glue Job - Processar com Spark**

Acessei o Glue Studio e criei uma nova job via Spark script editor:  https://us-east-1.console.aws.amazon.com/gluestudio/home?region=us-east-1#/jobs
Ele dá o seguinte boilerplate:

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
job.commit()
```

Pode ser carregado o arquivo `glue_job.py` onde já tenho o job codado.

Foi necessário criar uma role no IAM para permitir o Glue de acessar o bucket S3. Para facilitar o teste, Apliquei as policys gerenciadas `AmazonS3FullAccess` e `AWSGlueServiceRole`. Idealmente deveria ser criado uma política que desse acesso à apenas o bucket e ações necessárias (Incluindo o DeleteObject devido ao modo como o Glue cria pastas temporárias)

Ao rodar o job, deve ter sido criado a estrutura de pastas específica do exercicio.

**Criar o crawler do Glue Data Catalog e consumir no Athena**

Sem mistérios. Adicionar o novo crawler para ler a pasta `customerzone`. Criei uma base `microdados_enem`.

No Athena, antes de rodar as querys, criei uma pasta no bucket para salvar o resultado das consultas.
Junto dos microdados, tem um arquivo do dicionário de dados que utilizei para entender o que é cada campo.

Segue algumas consultas que utilizei de exemplo no Athena:

- Média da prova de matemática entre as mulheres
```sql
select
  avg(nu_nota_mt)
from "enem"
where "tp_sexo" = 'F'
```

- Média da prova de ciências humanas entre os homens que estudaram em SP
```sql
select
  avg(nu_nota_ch)
from "enem"
where "tp_sexo" = 'M'
  and "sg_uf_esc" = 'SP'
```

- Média da prova de Ciências Humanas de quem estudou em Natal
```sql
select
  avg(nu_nota_ch)
from "enem"
where "no_municipio_esc" = 'Natal'
```

- Municípios que viram a maior média em Matemática
```sql
select
  avg(nu_nota_mt),
  "no_municipio_esc"
from "enem"
group by "no_municipio_esc"
order by 1 DESC
```

- Quantidade de alunos que fizeram o Enem em Recife e que também estudaram lá
```sql
select
  count(*)
from "enem"
where "no_municipio_prova" = 'Recife'
  and "no_municipio_esc" = 'Recife'
```

- Nota média em Ciências Humanas dos alunos que estudaram numa escola no estado de Santa Catarina e possuem PELO MENOS 1 banheiro em casa
```sql
select
  avg("nu_nota_ch")
from "enem"
where "sg_uf_esc" = 'SC'
  and "q008" <> 'A'
```

- Nota média em matemática dos alunos cuja mãe possui PELO MENOS o ensino superior completo, do sexo feminino que estudaram numa escola em Belo Horizonte
```sql
select
  avg("nu_nota_mt")
from "enem"
where "no_municipio_esc" = 'Belo Horizonte'
  and "tp_sexo" = 'F'
  and "q002" in ('F','G')
```