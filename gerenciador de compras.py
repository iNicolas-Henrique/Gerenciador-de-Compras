import flet as ft
import json
import os

ARQUIVO = "compras.json"


def carregar_compras():
    # Carrega a lista que já foi salva.
    if not os.path.exists(ARQUIVO):
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if isinstance(dados, list):
            return dados
    except (json.JSONDecodeError, OSError):
        pass

    return []


def salvar_compras(compras):
    # Salva a lista no arquivo sempre que alguma coisa muda.
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(compras, arquivo, ensure_ascii=False, indent=4)


def main(page: ft.Page):
    page.title = "Gerenciador de Compras"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 920
    page.window.height = 720
    page.window.resizable = True
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_100

    compras = carregar_compras()
    editando = None

    produto = ft.TextField(label="Produto", expand=True)
    categoria = ft.TextField(label="Categoria", expand=True)

    quantidade = ft.TextField(
        label="Quantidade",
        expand=True
    )

    valor = ft.TextField(
        label="Valor unitário",
        expand=True
    )

    status = ft.Dropdown(
        label="Status",
        value="Pendente",
        expand=True,
        options=[
            ft.DropdownOption(key="Pendente"),
            ft.DropdownOption(key="Comprado")
        ]
    )

    observacao = ft.TextField(
        label="Observação",
        multiline=True,
        min_lines=2,
        max_lines=4
    )

    busca = ft.TextField(
        label="Buscar produto",
        expand=True
    )

    filtro = ft.Dropdown(
        label="Filtrar",
        value="Todos",
        width=180,
        options=[
            ft.DropdownOption(key="Todos"),
            ft.DropdownOption(key="Pendente"),
            ft.DropdownOption(key="Comprado")
        ]
    )

    mensagem = ft.Text()
    total_itens = ft.Text(weight=ft.FontWeight.BOLD)
    total_valor = ft.Text(weight=ft.FontWeight.BOLD)
    lista = ft.Column(spacing=10)

    def limpar_campos():
        produto.value = ""
        categoria.value = ""
        quantidade.value = ""
        valor.value = ""
        status.value = "Pendente"
        observacao.value = ""

    def converter_valor(texto):
        # Aceita valor digitado com vírgula também.
        texto = texto.strip().replace(",", ".")
        return float(texto)

    def atualizar_totais():
        # Soma quantidade x valor de cada item.
        total = 0

        for compra in compras:
            total += compra["quantidade"] * compra["valor"]

        total_itens.value = f"Itens cadastrados: {len(compras)}"
        total_valor.value = f"Total estimado: R$ {total:.2f}".replace(".", ",")

    def listar_compras(e=None):
        # Atualiza a lista de acordo com a busca e o filtro.
        lista.controls.clear()
        texto = busca.value.strip().lower()
        encontrados = 0

        for i, compra in enumerate(compras):
            if texto and texto not in compra["produto"].lower():
                continue

            if filtro.value != "Todos" and compra["status"] != filtro.value:
                continue

            encontrados += 1

            valor_unitario = f"R$ {compra['valor']:.2f}".replace(".", ",")
            subtotal = compra["quantidade"] * compra["valor"]
            subtotal_texto = f"R$ {subtotal:.2f}".replace(".", ",")

            detalhes = ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                compra["produto"],
                                size=18,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(compra["status"])
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Text(
                        f"Categoria: {compra['categoria']} | "
                        f"Quantidade: {compra['quantidade']}"
                    ),
                    ft.Text(
                        f"Valor unitário: {valor_unitario} | "
                        f"Subtotal: {subtotal_texto}"
                    ),
                    ft.Text(
                        "Observação: " + (
                            compra["observacao"]
                            if compra["observacao"]
                            else "Sem observação"
                        )
                    ),
                    ft.Row(
                        controls=[
                            ft.Button(
                                content="Editar",
                                data=i,
                                on_click=editar
                            ),
                            ft.Button(
                                content="Excluir",
                                data=i,
                                on_click=excluir
                            )
                        ]
                    )
                ],
                spacing=6
            )

            lista.controls.append(
                ft.Container(
                    content=detalhes,
                    bgcolor=ft.Colors.WHITE,
                    padding=15,
                    border_radius=8
                )
            )

        atualizar_totais()

        if encontrados == 0:
            lista.controls.append(
                ft.Container(
                    content=ft.Text("Nenhuma compra encontrada."),
                    bgcolor=ft.Colors.WHITE,
                    padding=15,
                    border_radius=8
                )
            )

        page.update()

    def salvar(e):
        nonlocal editando

        if (
            not produto.value.strip()
            or not categoria.value.strip()
            or not quantidade.value.strip()
            or not valor.value.strip()
        ):
            mensagem.value = "Preencha os campos obrigatórios."
            mensagem.color = ft.Colors.RED
            page.update()
            return

        # Confere se quantidade e valor são números válidos.
        try:
            qtd = int(quantidade.value)
            preco = converter_valor(valor.value)

            if qtd <= 0 or preco < 0:
                raise ValueError
        except ValueError:
            mensagem.value = "Quantidade ou valor inválido."
            mensagem.color = ft.Colors.RED
            page.update()
            return

        compra = {
            "produto": produto.value.strip(),
            "categoria": categoria.value.strip(),
            "quantidade": qtd,
            "valor": preco,
            "status": status.value,
            "observacao": observacao.value.strip()
        }

        # Se não estiver editando, adiciona uma nova compra.
        if editando is None:
            compras.append(compra)
            mensagem.value = "Compra cadastrada."
        else:
            compras[editando] = compra
            editando = None
            mensagem.value = "Compra atualizada."

        mensagem.color = ft.Colors.GREEN

        salvar_compras(compras)
        limpar_campos()
        listar_compras()

    def editar(e):
        nonlocal editando

        # Joga os dados da compra de volta nos campos.
        editando = int(e.control.data)
        compra = compras[editando]

        produto.value = compra["produto"]
        categoria.value = compra["categoria"]
        quantidade.value = str(compra["quantidade"])
        valor.value = str(compra["valor"]).replace(".", ",")
        status.value = compra["status"]
        observacao.value = compra["observacao"]

        mensagem.value = "Alterando compra."
        mensagem.color = ft.Colors.BLUE
        page.update()

    def excluir(e):
        nonlocal editando

        # Pega a posição da compra que vai ser excluída.
        posicao = int(e.control.data)
        compras.pop(posicao)

        editando = None
        limpar_campos()
        salvar_compras(compras)

        mensagem.value = "Compra excluída."
        mensagem.color = ft.Colors.RED
        listar_compras()

    def limpar(e):
        nonlocal editando

        editando = None
        limpar_campos()
        mensagem.value = ""
        page.update()

    # Busca e filtro atualizam a lista na hora.
    busca.on_change = listar_compras
    filtro.on_select = listar_compras

    titulo = ft.Text(
        "Gerenciador de Compras",
        size=27,
        weight=ft.FontWeight.BOLD
    )

    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Nova compra",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Row(
                    controls=[
                        produto,
                        categoria
                    ]
                ),
                ft.Row(
                    controls=[
                        quantidade,
                        valor,
                        status
                    ]
                ),
                observacao,
                ft.Row(
                    controls=[
                        ft.Button(content="Salvar", on_click=salvar),
                        ft.Button(content="Limpar", on_click=limpar)
                    ]
                ),
                mensagem
            ],
            spacing=12
        ),
        bgcolor=ft.Colors.WHITE,
        padding=18,
        border_radius=10
    )

    area_busca = ft.Row(
        controls=[
            busca,
            filtro
        ]
    )

    cabecalho_lista = ft.Row(
        controls=[
            ft.Text(
                "Lista de compras",
                size=20,
                weight=ft.FontWeight.BOLD
            ),
            ft.Column(
                controls=[
                    total_itens,
                    total_valor
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.END
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    conteudo_interno = ft.Column(
        controls=[
            titulo,
            ft.Text("Cadastre e acompanhe os itens da sua lista de compras."),
            formulario,
            cabecalho_lista,
            area_busca,
            lista
        ],
        spacing=16
    )

    # Deixa a tela rolável quando a lista ficar maior.
    conteudo = ft.Column(
        controls=[
            ft.Container(
                content=conteudo_interno,
                padding=ft.Padding.only(right=18)
            )
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    page.add(conteudo)
    listar_compras()


if __name__ == "__main__":
    ft.run(main)
